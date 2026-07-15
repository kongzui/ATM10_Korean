#!/usr/bin/env python3
"""Mekanism 전용 KubeJS 툴팁과 Ponder 표시 문구를 빌드한다."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from local_paths import PROJECT_ROOT, resolve_source_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FILES = (
    "Mekanism-Tooltips.js",
    "ponder/induction_mek.js",
    "ponder/fission_mek.js",
    "ponder/fusion_reactor.js",
    "ponder/fission_mek_logic.js",
    "ponder/fission_mek_fuelrod.js",
    "ponder/fission_mek_port.js",
    "ponder/sps.js",
    "ponder/turbine_mek.js",
    "ponder/fusion_activate.js",
)

REPLACEMENTS = {
    "Increased Energy Consumption!": "에너지 소모량 증가!",
    "Increased Energy Capacity": "에너지 용량 증가",
    "Increased Energy Capacity!": "에너지 용량 증가!",
    "Increased Attack Speed & Damage!": "공격 속도와 피해 증가!",
    "Increased Energy Capacity & Production!": "에너지 용량과 생산량 증가!",
    "Decreased Energy Production!": "에너지 생산량 감소!",
    "Increased Fuel Consumption!": "연료 소모량 증가!",
    "Decreased Fuel Consumption!": "연료 소모량 감소!",
    "Increased Production Speed!": "생산 속도 증가!",
    "Increased Machine Boost!": "기계 성능 향상!",
    "Increased Decay Rate!": "붕괴 속도 증가!",
    "Waste -> Polonium buffed!": "핵폐기물 → 폴로늄 생산량 증가!",
    "Waste -> Plutonium buffed!": "핵폐기물 → 플루토늄 생산량 증가!",
    "Decreased Energy Consumption!": "에너지 소모량 감소!",
    "Mekanism: Induction Matrix": "Mekanism: 유도 매트릭스",
    "The Induction Matrix is used to store tons of Power.": (
        "유도 매트릭스는 대량의 에너지를 저장합니다."
    ),
    "The Edges Must Be Casings": "모서리는 반드시 케이싱으로 만드세요.",
    "The Faces Can Be Either Casings Or Structural Glass.": (
        "면에는 케이싱이나 구조용 유리를 사용할 수 있습니다."
    ),
    "Ports Are Used To Transfer Power.": "포트는 에너지를 전송합니다.",
    "Ports Can Be Changed Using A Configurator.": (
        "설정 장치로 포트의 모드를 변경할 수 있습니다."
    ),
    "Induction Cells Are Used To Increase Power Storage.": (
        "유도 셀은 에너지 저장 용량을 늘립니다."
    ),
    "Induction Providers Are Used To Increase Power Transfer Rate.": (
        "유도 공급기는 에너지 전송 속도를 높입니다."
    ),
    "The Matrix Must Have One Cell and One Provider.": (
        "매트릭스에는 유도 셀과 유도 공급기가 하나씩 있어야 합니다."
    ),
    "Mekanism Fission Reactor": "Mekanism 핵분열로",
    "The Walls Can Be Either Casings Or Glass": (
        "벽에는 케이싱이나 원자로 유리를 사용할 수 있습니다."
    ),
    "Place Fuel Assembly Blocks Inside To Make The Fuel Rods": (
        "내부에 핵분열 연료 집합체를 배치해 연료봉을 만드세요."
    ),
    "Place Control Rod Assembly At The Top Of Each Fuel Rod": (
        "각 연료봉 위에 제어봉 집합체를 배치하세요."
    ),
    "Mekanism Fusion Reactor": "Mekanism 핵융합로",
    "The Fusion Reactor can be used to generate millions of RF per tick.": (
        "핵융합로는 틱당 수백만 RF를 생산할 수 있습니다."
    ),
    "Ports Can Be Changed Using A Configurator": (
        "설정 장치로 포트의 모드를 변경할 수 있습니다."
    ),
    "The Fusion Reactor is built using this pattern for each face.": (
        "핵융합로의 각 면을 이 형태로 만드세요."
    ),
    "You will need a port for exporting power.": ("에너지를 출력할 포트가 필요합니다."),
    "The Laser Matrix is used to kickstart the reactor.": (
        "레이저 초점 매트릭스로 반응기를 가동합니다."
    ),
    "The Fusion Reactor Controller must be placed in the middle of the top face.": (
        "핵융합로 제어기는 윗면 중앙에 배치해야 합니다."
    ),
    "You will need two ports for inputting Deuterium": (
        "중수소를 입력할 포트 두 개가 필요하고"
    ),
    "and Tritium.": "삼중수소도 입력해야 합니다.",
    "Mekanism Fission Reactor: Logic Adapters": "Mekanism 핵분열로: 로직 어댑터",
    "Logic Adapters allow Redstone Control for Reactors.": (
        "로직 어댑터를 사용하면 레드스톤으로 반응기를 제어할 수 있습니다."
    ),
    "Right Click to Open Configuration Settings": "우클릭해 설정 화면을 여세요.",
    "With two, you can set up a Fail Safe that can shut off the Reactor under certain conditions.": (
        "두 개를 사용하면 특정 조건에서 반응기를 정지하는 안전장치를 구성할 수 있습니다."
    ),
    "Set this one to Activation": "이 어댑터는 가동으로 설정하세요.",
    "Set this one to Damage Critical.": "이 어댑터는 심각한 피해로 설정하세요.",
    "When the Reactor has Critical Damage, it will give off a redstone signal.": (
        "반응기가 심각한 피해를 입으면 레드스톤 신호를 출력합니다."
    ),
    "We can use this to activate a piston with gravel or sand on it to activate an Observer.": (
        "이 신호로 자갈이나 모래를 받친 피스톤을 움직여 관측기를 작동시킬 수 있습니다."
    ),
    "This is an Oberserver facing towards the Gravel. The Gravel will activate it and turn off the reactor.": (
        "관측기가 자갈을 향하도록 배치하세요. 자갈이 관측기를 작동시켜 반응기를 끕니다."
    ),
    "Mekanism Fission Reactor: Fuel Assembly": "Mekanism 핵분열로: 연료 집합체",
    "Fuel Rods are created with several Fission Fuel Assembly blocks with a Control Rod Assembly on top.": (
        "핵분열 연료 집합체를 여러 개 쌓고 맨 위에 제어봉 집합체를 놓으면 연료봉이 됩니다."
    ),
    "Control Rod Assembly blocks are placed 1 block from the ceiling.": (
        "제어봉 집합체는 천장에서 한 블록 아래에 배치하세요."
    ),
    "Fuel Rods Cannot Touch": "연료봉끼리는 맞닿을 수 없습니다.",
    "Multiple Fuel Rods work best in a checkerboard pattern.": (
        "연료봉이 여러 개라면 바둑판 모양으로 배치하는 것이 좋습니다."
    ),
    "Mekanism Fission Reactor: Ports": "Mekanism 핵분열로: 포트",
    "A Reactor Needs At Least 4 Ports": "반응기에는 포트가 최소 4개 필요합니다.",
    "Required Ports:": "필요한 포트:",
    "Input Coolant": "냉각재 입력",
    "Input Fuel": "연료 입력",
    "Output Waste": "핵폐기물 출력",
    "Output Heated Coolant": "가열된 냉각재 출력",
    "Mekanism: Supercritical Phase Shifter (SPS)": (
        "Mekanism: 초임계 위상 변환기(SPS)"
    ),
    "The SPS converts Polonium into Antimatter Gas using a large amount of power": (
        "SPS는 막대한 에너지를 사용해 폴로늄을 반물질로 변환합니다."
    ),
    "The SPS is built using this pattern for each face.": "SPS의 각 면을 이 형태로 만드세요.",
    "On one side, you will need a Port in the middle to input power.": (
        "한쪽 면 중앙에는 에너지를 입력할 포트가 필요합니다."
    ),
    "On the inside, place a Supercharged Coil on the Port.": (
        "내부에서는 포트에 과충전 코일을 붙여 배치하세요."
    ),
    "You can also use two Supercharged Coils for max power usage.": (
        "과충전 코일을 두 개 사용하면 최대 속도로 에너지를 투입할 수 있습니다."
    ),
    "You will need one Port for inputting Polonium.": "폴로늄 입력용 포트가 하나 필요합니다.",
    "And another for exporting Antimatter Gas.": "다른 포트로 반물질을 출력하세요.",
    "Mekanism: Industrial Turbine": "Mekanism: 산업용 터빈",
    "The Industrial Turbine uses Heated Coolant to create Power.": (
        "산업용 터빈은 가열된 냉각재로 에너지를 생산합니다."
    ),
    "The edges must be made of Turbine Casings.": "모서리는 터빈 케이싱으로 만드세요.",
    "The faces can be Turbine Casings, Structural Glass, Valves, or Vents.": (
        "면에는 터빈 케이싱, 구조용 유리, 터빈 밸브, 증기 배출구를 사용할 수 있습니다."
    ),
    "Turbine Valves pump in Steam, or export Power.": (
        "터빈 밸브로 증기를 입력하거나 에너지를 출력합니다."
    ),
    "Turbine Rotors must be placed in the middle. Each Rotor uses 2 Turbine Blades.": (
        "터빈 로터는 중앙에 배치하세요. 로터 하나마다 터빈 블레이드 2개를 장착합니다."
    ),
    "A Rotational Complex must be placed on top of the Turbine Rotor.": (
        "터빈 로터 위에 회전 기구를 배치하세요."
    ),
    "Pressure Dispersers must fill the layer around the Rotational Complex.": (
        "회전 기구 주변 층을 압력 분산기로 채우세요."
    ),
    "Starting on this layer, Turbine Vents can be used for the outer faces. These also export Water from the Turbine.": (
        "이 층부터 바깥 면에 증기 배출구를 사용할 수 있습니다. 증기 배출구는 터빈에서 물도 출력합니다."
    ),
    "Electromagnetic Coils are placed on top of the Rotational Complex.": (
        "회전 기구 위에 전자기 코일을 배치하세요."
    ),
    "A max of 5 can be placed. They either must connect to each other, or be touching the Rotational Complex.": (
        "전자기 코일은 최대 5개까지 배치할 수 있으며, 서로 연결되거나 회전 기구에 닿아야 합니다."
    ),
    "Saturating Condensers are used to convert Steam back into Water. These are not required, but must be placed on or above the Coil Layer.": (
        "포화 응축기는 증기를 다시 물로 바꿉니다. 필수 부품은 아니지만 코일 층이나 그 위에 배치해야 합니다."
    ),
    "The Top Face can be replaced with Turbine Vents, if needed.": (
        "필요하면 윗면을 증기 배출구로 채울 수 있습니다."
    ),
    "Mekanism Fusion Reactor: Activation": "Mekanism 핵융합로: 가동",
    "To activate the Fusion Reactor, we will need a few things.": (
        "핵융합로를 가동하려면 몇 가지가 필요합니다."
    ),
    "You will need to put a Hohlraum filled with D-T fuel in the Controller.": (
        "제어기에 D-T 연료로 채운 홀로륨을 넣으세요."
    ),
    "You will need to shoot 400MRF using Lasers into the Laser Matrix.": (
        "레이저 초점 매트릭스에 레이저로 400MRF를 발사해야 합니다."
    ),
    "The Laser Amplifier needs to have the Red face pointing towards the Matrix.": (
        "레이저 증폭기의 빨간 면이 매트릭스를 향하게 하세요."
    ),
    "You will also need to give the Reactor fuel.": "반응기에 연료도 공급해야 합니다.",
    "For Deuterium": "중수소 입력",
    "For Tritium.": "삼중수소 입력",
    "The Reactor mixes the D-T fuel at a set rate when they are pumped in separately.": (
        "중수소와 삼중수소를 따로 주입하면 반응기가 설정된 속도로 D-T 연료를 혼합합니다."
    ),
}

VISIBLE_PATTERNS = (
    re.compile(r"\.scene\([^,]+,\s*(['\"])(.*?)\1"),
    re.compile(r"scene\.text\(\d+,\s*(['\"])(.*?)\1"),
    re.compile(r"\.showText\(\d+\)\.text\((['\"])(.*?)\1\)"),
    re.compile(r"Text\.(?:red|green)\((['\"])(.*?)\1\)"),
)
ALLOWED_TERMS = re.compile(r"Mekanism|SPS|MRF|RF|D-T")


def visible_strings(text: str) -> list[str]:
    values: list[str] = []
    for pattern in VISIBLE_PATTERNS:
        values.extend(match.group(2) for match in pattern.finditer(text))
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path)
    args = parser.parse_args()
    instance = resolve_source_root(args.instance)
    source_root = instance / "kubejs/client_scripts"
    output_root = PROJECT_ROOT / "output/overrides/kubejs/client_scripts"
    seen = {source: 0 for source in REPLACEMENTS}
    outputs: list[str] = []
    remaining: list[dict[str, str]] = []
    for relative in FILES:
        source = source_root / relative
        text = source.read_text(encoding="utf-8-sig")
        for english in sorted(REPLACEMENTS, key=len, reverse=True):
            korean = REPLACEMENTS[english]
            count = text.count(english)
            if count:
                seen[english] += count
                text = text.replace(english, korean)
        had_final_newline = text.endswith(("\n", "\r"))
        text = "\n".join(line.rstrip() for line in text.splitlines())
        if had_final_newline:
            text += "\n"
        destination = output_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")
        outputs.append(str(destination.relative_to(PROJECT_ROOT)))
        for value in visible_strings(text):
            inspected = ALLOWED_TERMS.sub("", value)
            if re.search(r"[A-Za-z]{3,}", inspected):
                remaining.append({"file": relative, "value": value})
    missing = [source for source, count in seen.items() if count == 0]
    if missing or remaining:
        raise ValueError(
            json.dumps(
                {"missing_source_literals": missing, "remaining_latin": remaining},
                ensure_ascii=False,
                indent=2,
            )
        )
    report = {
        "files": outputs,
        "translated_occurrences": sum(seen.values()),
        "remaining_latin": 0,
    }
    report_path = PROJECT_ROOT / "working/mekanism/extras_validation.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
