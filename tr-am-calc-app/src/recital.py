from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Recital:
    gymnasts: int
    spectators_per_gymnast: float
    ticket_price: float
    one_drive_transportation_cost: int
    coaches: int
    coaches_salary: int

    def __post_init__(self):
        if self.gymnasts <= 1:
            raise ValueError("gymnasts must be > 0")

    @property
    def tot_spectators(self) -> float:
        return self.spectators_per_gymnast * self.gymnasts

    @property
    def tot_tickets_sold(self) -> float:
        return self.tot_spectators * self.ticket_price

    def tot_coaches_cost(self) -> float:
        return self.coaches * self.coaches_salary