import json
from lib2to3.pytree import convert
from odoo import api, fields, models, tools, _
from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import requests


_logger = logging.getLogger(__name__)
MONTH_LIST= [('1', 'Enero'), 
        ('2', 'Febrero'), ('3', 'Marzo'), 
        ('4', 'Abril'), ('5', 'Mayo'), 
        ('6', 'Junio'), ('7', 'Julio'), 
        ('8', 'Agosto'), ('9', 'Septiembre'), 
        ('10', 'Octubre'), ('11', 'Noviembre'),
        ('12', 'Diciembre')]

STATES = {'draft': [('readonly', False)]}


class Compañia(models.Model):
    _inherit = 'res.company'

    mutualidad_id = fields.Many2one(comodel_name='hr.mutual', string='MUTUAL')
    ccaf_id = fields.Many2one(comodel_name='hr.ccaf', string='CCAF')    
    caja_compensacion = fields.Float(string='Caja Compensación',help="Caja de Compensacion")
    mutual_seguridad = fields.Float(string='Mutualidad', help="Mutual de Seguridad")
    zona_extrema = fields.Boolean(string='Zona Extrema', help='Indica si la empresa esta ubicada en zona extrema')
    sueldo_grado_1A = fields.Integer(string='Sueldo grado 1-A')
    porc_zona = fields.Float(string='% Tope Zona')
    tope_zona = fields.Integer(compute='_compute_tope_zona', string='Tope Zona')
    
    @api.depends('sueldo_grado_1A','porc_zona')
    def _compute_tope_zona(self):
        if self.sueldo_grado_1A and self.porc_zona:
            self.tope_zona=round(self.sueldo_grado_1A*(self.porc_zona/100),0) 
            print(round(self.sueldo_grado_1A*(self.porc_zona/100),0) )            


class hr_indicadores_previsionales(models.Model):

    _name = 'hr.indicadores'
    _description = 'Indicadores Previsionales'

    name = fields.Char('Nombre')
    state = fields.Selection([
        ('draft','Borrador'),
        ('done','Validado'),
        ], string=u'Estado', readonly=True, default='draft')
    asignacion_familiar_primer = fields.Float(
        'Asignación Familiar Tramo 1', 
        readonly=True, states=STATES,
        help="Asig Familiar Primer Tramo")
    asignacion_familiar_segundo = fields.Float(
        'Asignación Familiar Tramo 2', 
        readonly=True, states=STATES,
        help="Asig Familiar Segundo Tramo")
    asignacion_familiar_tercer = fields.Float(
        'Asignación Familiar Tramo 3', 
        readonly=True, states=STATES,
        help="Asig Familiar Tercer Tramo")
    asignacion_familiar_monto_a = fields.Float(
        'Monto Tramo Uno', readonly=True, states=STATES, help="Monto A")
    asignacion_familiar_monto_b = fields.Float(
        'Monto Tramo Dos', readonly=True, states=STATES, help="Monto B")
    asignacion_familiar_monto_c = fields.Float(
        'Monto Tramo Tres', readonly=True, states=STATES, help="Monto C")
    contrato_plazo_fijo_empleador = fields.Float(
        'Contrato Plazo Fijo Empleador', 
        readonly=True, states=STATES,
        help="Contrato Plazo Fijo Empleador")
    contrato_plazo_fijo_trabajador = fields.Float(
        'Contrato Plazo Fijo Trabajador', 
        readonly=True, states=STATES,
        help="Contrato Plazo Fijo Trabajador")    
    contrato_plazo_indefinido_empleador = fields.Float(
        'Contrato Plazo Indefinido Empleador', 
        readonly=True, states=STATES,
        help="Contrato Plazo Fijo")
    contrato_plazo_indefinido_empleador_otro = fields.Float(
        'Contrato Plazo Indefinido 11 anos o mas', 
        readonly=True, states=STATES,
        help="Contrato Plazo Indefinido 11 anos Empleador")
    contrato_plazo_indefinido_trabajador_otro = fields.Float(
        'Contrato Plazo Indefinido 11 anos o mas', 
        readonly=True, states=STATES,
        help="Contrato Plazo Indefinido 11 anos Trabajador")
    contrato_plazo_indefinido_trabajador = fields.Float(
        'Contrato Plazo Indefinido Trabajador', 
        readonly=True, states=STATES,
        help="Contrato Plazo Indefinido Trabajador")
    caja_compensacion = fields.Float(
        'Caja Compensación', 
        readonly=True, states=STATES,
        help="Caja de Compensacion")
    deposito_convenido = fields.Float(
        'Deposito Convenido', readonly=True, states=STATES, help="Deposito Convenido")
    fonasa = fields.Float('Fonasa', readonly=True, states=STATES, help="Fonasa")
    mutual_seguridad = fields.Float(
        'Mutualidad', readonly=True, states=STATES, help="Mutual de Seguridad")
    isl = fields.Float(
        'ISL', readonly=True, states=STATES, help="Instituto de Seguridad Laboral")
    pensiones_ips = fields.Float(
        'Pensiones IPS', readonly=True, states=STATES, help="Pensiones IPS")
    sueldo_minimo = fields.Float(
        'Trab. Dependientes e Independientes', readonly=True, states=STATES, help="Sueldo Minimo")
    sueldo_minimo_otro = fields.Float(
        'Menores de 18 y Mayores de 65:', 
        readonly=True, states=STATES,
        help="Sueldo Mínimo para Menores de 18 y Mayores a 65")
    tasa_afp_cuprum = fields.Float(
        'Cuprum', readonly=True, states=STATES, help="Tasa AFP Cuprum")
    tasa_afp_capital = fields.Float(
        'Capital', readonly=True, states=STATES, help="Tasa AFP Capital")
    tasa_afp_provida = fields.Float(
        'ProVida', readonly=True, states=STATES, help="Tasa AFP Provida")
    tasa_afp_modelo = fields.Float(
        'Modelo', readonly=True, states=STATES, help="Tasa AFP Modelo")
    tasa_afp_planvital = fields.Float(
        'PlanVital', readonly=True, states=STATES, help="Tasa AFP PlanVital")
    tasa_afp_habitat = fields.Float(
        'Habitat',  help="Tasa AFP Habitat")
    tasa_afp_uno = fields.Float(
        'Uno', help="Tasa AFP Uno")
    tasa_sis_cuprum = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa SIS Cuprum")
    tasa_sis_capital = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa SIS Capital")
    tasa_sis_provida = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa SIS Provida")
    tasa_sis_planvital = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa SIS PlanVital")
    tasa_sis_habitat = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa SIS Habitat")
    tasa_sis_modelo = fields.Float(
        'SIS',  help="Tasa SIS Modelo")
    tasa_sis_uno = fields.Float(
        'SIS', help="Tasa SIS Uno")
    tasa_independiente_cuprum = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa Independientes Cuprum")
    tasa_independiente_capital = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa Independientes Capital")
    tasa_independiente_provida = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa Independientes Provida")
    tasa_independiente_planvital = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa Independientes PlanVital")
    tasa_independiente_habitat = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa Independientes Habitat")
    tasa_independiente_modelo = fields.Float(
        'SIS',  help="Tasa Independientes Modelo")
    tasa_independiente_uno = fields.Float(
        'SIS', help="Tasa Independientes Uno")
    tope_anual_apv = fields.Float(
        'Tope Anual APV', readonly=True, states=STATES, help="Tope Anual APV")
    tope_mensual_apv = fields.Float(
        'Tope Mensual APV', readonly=True, states=STATES, help="Tope Mensual APV")
    tope_imponible_afp = fields.Float(
        'Tope imponible AFP', readonly=True, states=STATES, help="Tope Imponible AFP")
    tope_imponible_ips = fields.Float(
        'Tope Imponible IPS', readonly=True, states=STATES, help="Tope Imponible IPS")
    tope_imponible_salud = fields.Float(
        'Tope Imponible Salud', readonly=True, states=STATES,)
    tope_imponible_seguro_cesantia = fields.Float(
        'Tope Imponible Seguro Cesantía', 
        readonly=True, states=STATES,
        help="Tope Imponible Seguro de Cesantía")
    uf = fields.Float(
        'UF',  required=True, readonly=True, states=STATES, help="UF fin de Mes")
    utm = fields.Float(
        'UTM',  required=True, readonly=True, states=STATES, help="UTM Fin de Mes")
    uta = fields.Float('UTA', readonly=True, states=STATES, help="UTA Fin de Mes")
    uf_otros = fields.Float(
        'UF Otros', readonly=True, states=STATES, help="UF Seguro Complementario")
    mutualidad_id = fields.Many2one('hr.mutual', 'MUTUAL', readonly=True, states=STATES)
    ccaf_id = fields.Many2one('hr.ccaf', 'CCAF', readonly=True, states=STATES)
    month = fields.Selection(MONTH_LIST, string='Mes', required=True, readonly=True, states=STATES)
    year = fields.Integer('Año', required=True, default=datetime.now().strftime('%Y'), readonly=True, states=STATES)
    gratificacion_legal = fields.Boolean('Gratificación L. Manual', readonly=True, states=STATES)
    mutual_seguridad_bool = fields.Boolean('Mutual Seguridad', default=True, readonly=True, states=STATES)
    ipc = fields.Float(
        'IPC',  required=True, readonly=True, states=STATES, help="Indice de Precios al Consumidor (IPC)")
    
    @api.multi
    def action_done(self):
        self.write({'state': 'done'})
        return True
    
    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    @api.onchange('month')
    def get_name(self):
        self.name = str(self.month).replace('10', 'Octubre').replace('11', 'Noviembre').replace('12', 'Diciembre').replace('1', 'Enero').replace('2', 'Febrero').replace('3', 'Marzo').replace('4', 'Abril').replace('5', 'Mayo').replace('6', 'Junio').replace('7', 'Julio').replace('8', 'Agosto').replace('9', 'Septiembre') + " " + str(self.year)

    def find_between_r(self, s, first, last ):
        try:
            start = s.rindex( first ) + len( first )
            end = s.rindex( last, start )
            return s[start:end]
        except ValueError:
            return ""

    def find_month(self, s):
        if s == '1':
            return 'Enero'
        if s == '2':
            return 'Febrero'
        if s == '3':
            return 'Marzo'
        if s == '4':
            return 'Abril'
        if s == '5':
            return 'Mayo'
        if s == '6':
            return 'Junio'
        if s == '7':
            return 'Julio'
        if s == '8':
            return 'Agosto'
        if s == '9':
            return 'Septiembre'
        if s == '10':
            return 'Octubre'
        if s == '11':
            return 'Noviembre'
        if s == '12':
            return 'Diciembre'

    def find_month_month(self, s):
        if s == '1':
            return '01'
        if s == '2':
            return '02'
        if s == '3':
            return '03'
        if s == '4':
            return '04'
        if s == '5':
            return '05'
        if s == '6':
            return '06'
        if s == '7':
            return '07'
        if s == '8':
            return '08'
        if s == '9':
            return '09'
        if s == '10':
            return '10'
        if s == '11':
            return '11'
        if s == '12':
            return '12'


    @api.one
    def update_document(self):
        self.update_date = datetime.today()
        company=self.env.user.company_id
        mes=self.find_month_month(self.month)
        periodo=mes+str(self.year)
        if company.ccaf_id:
            self.ccaf_id=company.ccaf_id.id
            self.caja_compensacion=company.caja_compensacion
            self.fonasa=7-company.caja_compensacion
        else:
            self.fonasa=7
        if company.mutualidad_id:
            self.mutualidad_id=company.mutualidad_id.id
            self.mutual_seguridad=company.mutual_seguridad
            self.pensiones_ips=10
            self.tope_imponible_salud=7


        # try:
        #     html_doc = urlopen('https://www.previred.com/web/previred/indicadores-previsionales').read()
        #     soup = BeautifulSoup(html_doc, 'html.parser')

        #     letters = soup.find_all("table")

        #     def clear_string(cad):
        #         cad = cad.replace(".", '').replace("$", '').replace(" ", '')
        #         cad = cad.replace("Renta", '').replace("<", '').replace(">", '')
        #         cad = cad.replace("=", '').replace("R", '').replace("I", '').replace("%", '')
        #         cad = cad.replace(",", '.')
        #         cad = cad.replace("1ff8","")
        #         return cad
        # except ValueError:
        #     return ""

        def string_divide(cad, cad2, rounded):
            return round(float(cad) / float(cad2), rounded)

        url = "https://api.gael.cloud/general/public/previred/"+periodo
        payload={}
        headers = {}
        dict={}
        data = requests.request("GET", url, headers=headers, data=payload)
        dict = json.loads(data.text)
        print(float(dict['UFValPeriodo'].replace(",",".")))
        #try:
        # UF
        self.uf =float(dict['UFValPeriodo'].replace(",",".")) 

        # 1 UTM
        self.utm = int(dict['UTMVal'].replace(",00",""))

        # 1 UTA
        self.uta = int(dict['UTAVal'].replace(",00",""))

        # 3 RENTAS TOPES IMPONIBLES UF
        self.tope_imponible_afp = dict['RTIAfpUF'].replace(",",".")
        self.tope_imponible_ips = dict['RTIIpsUF'].replace(",",".")
        self.tope_imponible_seguro_cesantia = dict['RTISegCesUF'].replace(",",".")

        # 4 RENTAS TOPES IMPONIBLES
        self.sueldo_minimo = dict['RMITrabDepeInd'].replace(",",".")
        self.sueldo_minimo_otro = dict['RMIMen18May65'].replace(",",".")

        # Ahorro Previsional Voluntario
        self.tope_mensual_apv = int(dict['APVTopeMensUF'].replace(",","."))
        self.tope_anual_apv = int(dict['APVTopeAnuUF'].replace(",","."))

        # 5 DEPÓSITO CONVENIDO
        self.deposito_convenido = int(dict['DepConvenidoUF'].replace(",","."))

        # 6 RENTAS TOPES IMPONIBLES
        self.contrato_plazo_indefinido_empleador = dict['AFCCpiEmpleador'].replace(",",".")
        self.contrato_plazo_indefinido_trabajador = dict['AFCCpiTrabajador'].replace(",",".")
        self.contrato_plazo_fijo_empleador = dict['AFCCpfEmpleador'].replace(",",".")
        self.contrato_plazo_indefinido_empleador_otro = dict['AFCCpi11Empleador'].replace(",",".")

        # 7 ASIGNACIÓN FAMILIAR
        self.asignacion_familiar_monto_a = int(dict['AFamTramoAMonto'].replace(",","."))
        self.asignacion_familiar_monto_b = int(dict['AFamTramoBMonto'].replace(",","."))
        self.asignacion_familiar_monto_c = int(dict['AFamTramoCMonto'].replace(",","."))

        self.asignacion_familiar_primer = int(dict['AFamTramoAHasta'].replace(",","."))
        self.asignacion_familiar_segundo = int(dict['AFamTramoBHasta'].replace(",","."))
        self.asignacion_familiar_tercer = int(dict['AFamTramoCHasta'].replace(",","."))
        # 8 TASA COTIZACIÓN OBLIGATORIO AFP
        self.tasa_afp_capital = dict['AFPCapitalTasaDep'].replace(",",".")
        self.tasa_sis_capital = dict['AFPCapitalTasaSIS'].replace(",",".")

        self.tasa_afp_cuprum = dict['AFPCuprumTasaDep'].replace(",",".")
        self.tasa_sis_cuprum = dict['AFPCuprumTasaSIS'].replace(",",".")

        self.tasa_afp_habitat = dict['AFPHabitatTasaDep'].replace(",",".")
        self.tasa_sis_habitat = dict['AFPHabitatTasaSIS'].replace(",",".")

        self.tasa_afp_planvital = dict['AFPPlanVitalTasaDep'].replace(",",".")
        self.tasa_sis_planvital = dict['AFPPlanVitalTasaSIS'].replace(",",".")

        self.tasa_afp_provida = dict['AFPProVidaTasaDep'].replace(",",".")
        self.tasa_sis_provida = dict['AFPProVidaTasaSIS'].replace(",",".")

        self.tasa_afp_modelo = dict['AFPModeloTasaDep'].replace(",",".")
        self.tasa_sis_modelo = dict['AFPModeloTasaSIS'].replace(",",".")

        self.tasa_afp_uno = dict['AFPUnoTasaDep'].replace(",",".")
        self.tasa_sis_uno = dict['AFPUnoTasaSIS'].replace(",",".")

        self.tasa_independiente_capital = dict['AFPCapitalTasaInd'].replace(",",".")
        self.tasa_independiente_cuprum = dict['AFPCuprumTasaInd'].replace(",",".")
        self.tasa_independiente_habitat = dict['AFPHabitatTasaInd'].replace(",",".")
        self.tasa_independiente_planvital = dict['AFPPlanVitalTasaInd'].replace(",",".")
        self.tasa_independiente_provida = dict['AFPProVidaTasaInd'].replace(",",".")
        self.tasa_independiente_modelo = dict['AFPModeloTasaInd'].replace(",",".")
        self.tasa_independiente_uno = dict['AFPUnoTasaInd'].replace(",",".")

        #except ValueError:
        #    return ""
