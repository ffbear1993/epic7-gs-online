import json
from dataclasses import dataclass, asdict, field
from typing import List


@dataclass
class Main:
    type: str = None
    value: int = -1


@dataclass
class Substats:
    type: str = None
    value: int = -1
    rolls: int = None
    modified: bool = False


@dataclass
class AugmentedStats:
    Attack: int
    AttackPercent: int
    CriticalHitChancePercent: int
    CriticalHitDamagePercent: int
    Defense: int
    DefensePercent: int
    EffectResistancePercent: int
    EffectivenessPercent: int
    Health: int
    HealthPercent: int
    Speed: int
    mainType: str
    mainValue: int


@dataclass
class ReforgedStats:
    Attack: int
    AttackPercent: int
    CriticalHitChancePercent: int
    CriticalHitDamagePercent: int
    Defense: int
    DefensePercent: int
    EffectResistancePercent: int
    EffectivenessPercent: int
    Health: int
    HealthPercent: int
    Speed: int
    mainType: str
    mainValue: int


@dataclass
class GearItem:
    gear: str = None
    rank: str = None
    set: str = None
    enhance: int = -1
    level: int = -1
    main: Main = None
    substats: List[Substats] = None
    augmentedStats: AugmentedStats = field(init=False)
    reforgedStats: ReforgedStats = field(init=False)
    id: str = field(init=False)
    disableMods: bool = field(init=False)
    reforgeable: int = field(init=False)
    upgradeable: int = field(init=False)
    convertable: int = field(init=False)
    priority: int = field(init=False)
    wss: int = field(init=False)
    reforgedWss: int = field(init=False)
    dpsWss: int = field(init=False)
    supportWss: int = field(init=False)
    combatWss: int = field(init=False)
    duplicateId: str = field(init=False)
    allowedMods: str = field(init=False)

    @property
    def __dict__(self):
        return asdict(self)

    @property
    def json(self):
        return json.dumps(self.__dict__)

    def __post_init__(self):
        self.augmentedStats = AugmentedStats(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "", 0)
        self.reforgedStats = ReforgedStats(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "", 0)
        self.id = ""
        self.disableMods = ""
        self.reforgeable = 0
        self.upgradeable = 0
        self.convertable = 0
        self.priority = 0
        self.wss = 0
        self.reforgedWss = 0
        self.dpsWss = 0
        self.supportWss = 0
        self.combatWss = 0
        self.duplicateId = ""
        self.allowedMods = ""
