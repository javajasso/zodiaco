class Signo: 
    def __init__(self, dia, mes):
        self.dia = dia
        self.mes = mes
    
    def toDBCollection(self):
        return{
            'dia': self.dia,
            'mes': self.mes
        }
