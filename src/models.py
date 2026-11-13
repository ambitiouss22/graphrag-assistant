from typing import Literal
from pydantic import BaseModel

EntityType = Literal["Model", "Method", "Dataset", "Benchmark", "Organization", "Tool"]
RelType = Literal["USES", "EVALUATED_ON", "IMPROVES_ON", "DEVELOPED_BY", "PART_OF", "COMPARED_WITH"]


class Entity(BaseModel):
    name: str
    type: EntityType


class Relation(BaseModel):
    source: str
    relation: RelType
    target: str
    evidence: str


class Extraction(BaseModel):
    entities: list[Entity] = []
    relations: list[Relation] = []