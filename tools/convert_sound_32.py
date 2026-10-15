#!/usr/bin/env python3
"""
Convierte los datos de sonido precompilados de sm64coopdx (little-endian, palabras
de 64 bits) al formato de 32 bits (palabras de 4 bytes) que espera un build ARM de 32 bits.

Uso: convert_sound_32.py <carpeta_con sound_data.ctl, sound_data.tbl y sequences.bin>
Escribe los archivos convertidos en su lugar (deja copias *.64bit) y regenera los
archivos *.inc.c que incluye el codigo C.
"""
import struct
import sys
import os


def align(v, a):
    return (v + a - 1) & -a


def u32(b, o):
    return struct.unpack_from('<I', b, o)[0]


def u64(b, o):
    return struct.unpack_from('<Q', b, o)[0]


def read_seqfile64(d):
    magic, count = struct.unpack_from('<HH', d, 0)
    ents = [(u64(d, 8 + i * 16), u32(d, 8 + i * 16 + 8)) for i in range(count)]
    return magic, count, ents


# ---------------------------------------------------------------- bancos (ctl)

def parse_bank64(entry):
    nI, nD, shared, date = struct.unpack_from('<IIII', entry, 0)
    body = entry[16:]
    B = len(body)
    assert B % 16 == 0, "cuerpo del banco no alineado"

    drum_ptr = u64(body, 0)
    inst_ptrs = [u64(body, 8 + 8 * i) for i in range(nI)]
    table_end = align(8 + 8 * nI, 16)

    drums = []
    if nD:
        dt_off = B - align(8 * nD, 16)
        assert drum_ptr == dt_off, "puntero a tabla de percusion inesperado"
        drum_table = [u64(body, dt_off + 8 * i) for i in range(nD)]
        dstart = dt_off - align(32 * nD, 16)
        for k in range(nD):
            o = dstart + 32 * k
            assert drum_table[k] == o, "tabla de percusion inconsistente"
            assert body[o + 2] == 0 and body[o + 3] == 0 and u32(body, o + 4) == 0
            drums.append(dict(rel=body[o], pan=body[o + 1],
                              sample=u64(body, o + 8), tuning=bytes(body[o + 16:o + 20]),
                              env=u64(body, o + 24)))
        i_end = dstart
    else:
        assert drum_ptr == 0
        i_end = B

    # muestras (sample + book + loop), en secuencia
    samples = []
    pos = table_end
    while pos + 48 <= B:
        if u32(body, pos) != 0 or u32(body, pos + 4) != 0:
            break
        addr = u64(body, pos + 8)
        loop_p = u64(body, pos + 16)
        book_p = u64(body, pos + 24)
        size = u32(body, pos + 32)
        if book_p != pos + 48:
            break
        order, npred = struct.unpack_from('<ii', body, book_p)
        if order <= 0 or npred <= 0:
            break
        blen = align(8 + order * npred * 8 * 2, 16)
        if loop_p != book_p + blen:
            break
        count = struct.unpack_from('<i', body, loop_p + 8)[0]
        llen = 16 if count == 0 else 48
        samples.append(dict(old=pos, addr=addr, size=size,
                            book=bytes(body[book_p:book_p + blen]),
                            loop=bytes(body[loop_p:loop_p + llen])))
        pos = loop_p + llen
        assert pos % 16 == 0
    sample_starts = {s['old'] for s in samples}

    # envolventes + inicio de instrumentos
    env_starts = set()
    envs = []

    def valid_instr_region(istart):
        n = i_end - istart
        if n < 0 or n % 64:
            return False
        for o in range(istart, i_end, 64):
            if body[o] != 0 or u32(body, o + 4) != 0:
                return False
            if body[o + 1] > body[o + 2] or body[o + 2] > 127:
                return False
            if u64(body, o + 8) not in env_starts:
                return False
            for so in (o + 16, o + 32, o + 48):
                sa = u64(body, so)
                if u32(body, so + 12) != 0:
                    return False
                if sa != 0 and sa not in sample_starts:
                    return False
        return True

    p = pos
    while True:
        if valid_instr_region(p):
            istart = p
            break
        assert p < i_end, "no se encontro la region de instrumentos"
        q = p
        while True:
            delay = struct.unpack_from('>H', body, q)[0]
            q += 4
            if delay in (0, 0xFFFF, 0xFFFE, 0xFFFD):
                break
        env_starts.add(p)
        envs.append((p, bytes(body[p:align(q, 16)])))
        p = align(q, 16)

    insts = []
    for o in range(istart, i_end, 64):
        sounds = []
        for so in (o + 16, o + 32, o + 48):
            sounds.append((u64(body, so), bytes(body[so + 8:so + 12])))
        insts.append(dict(old=o, lo=body[o + 1], hi=body[o + 2], rel=body[o + 3],
                          env=u64(body, o + 8), sounds=sounds))

    return dict(hdr=(nI, nD, shared, date), nI=nI, nD=nD, inst_ptrs=inst_ptrs,
                samples=samples, envs=envs, insts=insts, drums=drums)


def build_bank(m, W):
    def P(v):
        return struct.pack('<I' if W == 4 else '<Q', v)
    X = b'' if W == 4 else b'\0\0\0\0'

    body = bytearray()

    def pad16():
        body.extend(b'\0' * (align(len(body), 16) - len(body)))

    def put(pos, data):
        body[pos:pos + len(data)] = data

    body += b'\0' * W                       # puntero a percusion
    tab_pos = len(body)
    body += b'\0' * (W * m['nI'])           # tabla de instrumentos
    pad16()

    smap = {}
    for s in m['samples']:
        smap[s['old']] = len(body)
        body += struct.pack('<I', 0) + X
        body += P(s['addr'])
        loop_pos = len(body)
        body += b'\0' * W
        book_pos = len(body)
        body += b'\0' * W
        body += struct.pack('<I', s['size'])
        pad16()
        book_addr = len(body)
        body += s['book']
        loop_addr = len(body)
        body += s['loop']
        put(book_pos, P(book_addr))
        put(loop_pos, P(loop_addr))

    emap = {}
    for old, data in m['envs']:
        emap[old] = len(body)
        body += data

    def sound(sa, tuning):
        return P(0 if sa == 0 else smap[sa]) + tuning + X

    imap = {}
    for ins in m['insts']:
        imap[ins['old']] = len(body)
        body += bytes([0, ins['lo'], ins['hi'], ins['rel']]) + X + P(emap[ins['env']])
        for sa, tu in ins['sounds']:
            body += sound(sa, tu)
    pad16()

    for i, old in enumerate(m['inst_ptrs']):
        put(tab_pos + W * i, P(0 if old == 0 else imap[old]))

    if m['nD']:
        dposes = []
        for d in m['drums']:
            dposes.append(len(body))
            body += bytes([d['rel'], d['pan'], 0, 0]) + X
            body += sound(d['sample'], d['tuning'])
            body += P(emap[d['env']])
        pad16()
        put(0, P(len(body)))
        for dp in dposes:
            body += P(dp)
        pad16()

    return struct.pack('<IIII', *m['hdr']) + bytes(body)


def build_seqfile(magic, entries_data, W):
    """entries_data: lista de bytes. Replica el formato de assemble_sound.py."""
    X = b'' if W == 4 else b'\0\0\0\0'
    count = len(entries_data)
    hdr_size = align(4 + (4 if W == 8 else 0) + count * 2 * W, 16)
    data = b''.join(entries_data)
    out = bytearray(struct.pack('<HH', magic, count) + X)
    off = hdr_size
    table = bytearray()
    for e in entries_data:
        table += struct.pack('<I' if W == 4 else '<Q', off) + struct.pack('<I', len(e)) + X
        off += len(e)
    out += table
    out += b'\0' * (hdr_size - len(out))
    out += data
    out += b'\0'
    out += b'\0' * (align(len(out), 64) - len(out))
    return bytes(out)


def convert_ctl(d, W=4):
    magic, count, ents = read_seqfile64(d)
    banks = [d[o:o + n] for o, n in ents]
    models = [parse_bank64(b) for b in banks]
    return build_seqfile(magic, [build_bank(m, W) for m in models], W), models, banks


def convert_header_only(d):
    """tbl y sequences.bin: solo cambia la cabecera; se conserva el inicio de los datos
    (y con el todos los desplazamientos absolutos usados por el resto del juego)."""
    magic, count, ents = read_seqfile64(d)
    data_start = align(8 + 16 * count, 16)
    assert all(o >= data_start for o, _ in ents), "offsets inesperados"
    hdr = bytearray(struct.pack('<HH', magic, count))
    for o, n in ents:
        hdr += struct.pack('<II', o, n)
    assert len(hdr) <= data_start
    hdr += b'\0' * (data_start - len(hdr))
    return bytes(hdr) + d[data_start:]


def write_inc(path, data):
    with open(path, 'w') as f:
        f.write(''.join('0x%X,' % b for b in data))
        f.write('\n')


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    sdir = sys.argv[1]
    for name in ('sound_data.ctl', 'sound_data.tbl', 'sequences.bin'):
        p = os.path.join(sdir, name)
        d = open(p, 'rb').read()
        magic = struct.unpack_from('<H', d, 0)[0]
        if name == 'sound_data.ctl':
            # comprobacion de ida y vuelta con el layout de 64 bits
            rt, _, _ = convert_ctl(d, 8)
            if rt != d:
                raise SystemExit("la reconstruccion de 64 bits no coincide con el original: abortando")
            new, _, _ = convert_ctl(d, 4)
        else:
            new = convert_header_only(d)
        if not os.path.exists(p + '.64bit'):
            os.replace(p, p + '.64bit')
        open(p, 'wb').write(new)
        write_inc(p + '.inc.c', new)
        print('%s: %d -> %d bytes (convertido a 32 bits)' % (name, len(d), len(new)))


if __name__ == '__main__':
    main()Enter
