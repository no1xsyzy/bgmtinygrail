from bgmtinygrail.bgmd.api import character_detail

if __name__ == '__main__':
    for cid in range(14805, 14817):
        detail = character_detail(cid)
        print(f"{detail.id}, {detail.name}, {detail.name_cn}")
