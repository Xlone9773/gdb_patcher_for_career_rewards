#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#gdb_patcher_for_career_rewards - Version 6.0
#Automated binary structure discovery and patch tool for legacy GDB local reward tables (v1.2.1).
#Employs signature scanning, float unpack verification, and padding filtering (256-multipliers constraint).
import sys, struct, shutil

def scan(data):
    out, i, n = [], 0, len(data)
    while i < n - 8:
        if data[i] == 1 and data[i+1] == 4 and \
           data[i+4] == 0 and data[i+5] == 0 and data[i+6] == 0 and data[i+7] == 0:
            lid = data[i+2] | (data[i+3] << 8)
            for j in range(i + 12, min(i + 48, n - 8)):
                if data[j] == 0x3F and data[j-1] == 0x80 and data[j-2] == 0 and data[j-3] == 0:
                    diff = struct.unpack_from('<f', data, j - 7)[0]
                    flag = struct.unpack_from('<I', data, j + 1)[0]
                    if 0.0 <= diff <= 1.5 and 50 <= flag <= 1000000:
                        # v6 排名匹配：50~50000 且非 256 倍数，取前 4
                        ranks = []
                        for k in range(j + 9, min(j + 100, n - 4)):
                            if data[k] == 0 and data[k + 3] == 0:
                                v = data[k+1] | (data[k+2] << 8)
                                if 50 <= v <= 50000 and v % 256 != 0:
                                    ranks.append((k + 1, v))
                                    if len(ranks) >= 4:
                                        break
                        out.append((i, lid, j - 7, j + 1, diff, flag, ranks))
                        break
            i += 8
        i += 1
    return out

def fmt_id(lid):
    return '0x%02X%02X' % (lid & 0xFF, (lid >> 8) & 0xFF)

def do_list(data, path):
    rows = scan(data)
    print(f'共 {len(rows)} 关')
    print(f'{"ID":<12}{"难度":<8}{"旗帜":<8}{"R1":<7}{"R2":<7}{"R3":<7}{"R4":<7}')
    for off, lid, da, fa, diff, flag, ranks in rows:
        rs = [str(v) for o, v in ranks]
        print(f'{fmt_id(lid):<12}{diff:<8.3f}{flag:<8}'
              f'{rs[0] if len(rs)>0 else "-":<7}{rs[1] if len(rs)>1 else "-":<7}'
              f'{rs[2] if len(rs)>2 else "-":<7}{rs[3] if len(rs)>3 else "-":<7}')

def do_patch(path, specs):
    data = bytearray(open(path, 'rb').read())
    rows = scan(data)
    by_id = {lid: (da, fa, ranks) for off, lid, da, fa, diff, flag, ranks in rows}
    for spec in specs:
        p = spec.split(':')
        lid = int(p[0], 0)
        if lid not in by_id:
            print(f'!! 未找到 {fmt_id(lid)}'); continue
        da, fa, ranks = by_id[lid]
        if len(p) >= 2:
            struct.pack_into('<I', data, fa, int(p[1]))
            print(f'[{fmt_id(lid)}] 旗帜奖励 -> {p[1]}')
        if len(p) >= 3:
            struct.pack_into('<f', data, da, float(p[2]))
            print(f'[{fmt_id(lid)}] 难度 -> {p[2]}')
        if len(p) >= 4:
            vals = p[3].split(',')
            for idx, val in enumerate(vals[:4]):
                if idx < len(ranks):
                    struct.pack_into('<H', data, ranks[idx][0], int(val))
                    print(f'[{fmt_id(lid)}] R{idx+1}(排名) -> {val}')
            if len(vals) > len(ranks):
                print(f'!! 警告: 只找到 {len(ranks)} 个排名字段，多余值未写入')
    shutil.copy(path, path + '.bak')
    open(path, 'wb').write(data)
    print(f'已写回 {path}（备份 .bak）')

def do_all(path, flag=None, diff=None, rank=None):
    data = bytearray(open(path, 'rb').read())
    rows = scan(data)
    for off, lid, da, fa, d, f, ranks in rows:
        if flag is not None: struct.pack_into('<I', data, fa, flag)
        if diff is not None: struct.pack_into('<f', data, da, diff)
        if rank is not None:
            for o, v in ranks: struct.pack_into('<H', data, o, rank)
    shutil.copy(path, path + '.bak')
    open(path, 'wb').write(data)
    print(f'已批量修改 {len(rows)} 关（旗帜={flag} 难度={diff} 排名={rank}）')

if __name__ == '__main__':
    a = sys.argv
    if len(a) < 3: print(__doc__); sys.exit(1)
    mode, path = a[1], a[2]
    if mode == 'list':
        do_list(open(path, 'rb').read(), path)
    elif mode == 'patch':
        do_patch(path, a[3:])
    elif mode == 'all':
        fl = int(a[a.index('--flag')+1]) if '--flag' in a else None
        df = float(a[a.index('--diff')+1]) if '--diff' in a else None
        rk = int(a[a.index('--rank')+1]) if '--rank' in a else None
        do_all(path, fl, df, rk)
    else:
        print(__doc__)
