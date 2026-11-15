import json

def get_plant_truth():
    from domains.equipment_state.demos.plant.rules import PLANT_TYPE_MAP
    return {"domain":"tune_domain","module":"plant","valid_type_ids":list(PLANT_TYPE_MAP.keys()),"type_desc":PLANT_TYPE_MAP}

def get_wall_truth():
    from world_state.src.domains.environment_state.rules import GOODWALL_TYPE_MAP
    return {"domain":"good_domain","module":"wall","valid_type_ids":list(GOODWALL_TYPE_MAP.keys()),"type_desc":GOODWALL_TYPE_MAP}

def get_all_truth():
    return [get_plant_truth(), get_wall_truth()]

def main():
    with open("src/test/cases.json","r",encoding="utf-8") as f:
        cases = json.load(f)
    truth_list = get_all_truth()
    truth_map = {t["module"]:t for t in truth_list}
    module_case_rec = {}
    for case in cases:
        m = case["module"]
        tid = case["expect_type_id"]
        if m not in module_case_rec:
            module_case_rec[m] = set()
        module_case_rec[m].add(tid)

    print("==================================================")
    print("          真值业务分支校验报告")
    print("==================================================")
    for mod_name, truth in truth_map.items():
        valid_ids = set(truth["valid_type_ids"])
        covered = module_case_rec.get(mod_name, set())
        missing = valid_ids - covered
        print(f"【模块：{mod_name}】")
        print(f"基准合法type_id: {sorted(list(valid_ids))}")
        print(f"已覆盖type_id: {sorted(list(covered))}")
        if missing:
            print(f"❌缺失分支type_id: {sorted(list(missing))}")
        else:
            print(f"❌缺失分支type_id: []")
        print()

if __name__ == "__main__":
    main()
