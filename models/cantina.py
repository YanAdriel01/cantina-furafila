from database.dao.item_dao import ItemDAO
from database.dao.pedido_dao import PedidoDAO
from database.dao.configuracao_dao import ConfiguracaoDAO

class Cantina:
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.item_dao = ItemDAO(db_manager)
        self.pedido_dao = PedidoDAO(db_manager)
        self.config_dao = ConfiguracaoDAO(db_manager)
    
    def get_status(self):
        return self.config_dao.get_status_cantina()
    
    def set_status(self, status):
        self.config_dao.set_status_cantina(status)
    
    def get_cardapio(self):
        return self.item_dao.listar_ativos()
    
    def buscar_item(self, nome_item):
        return self.item_dao.buscar_por_nome(nome_item)
    
    def buscar_item_por_id(self, item_id):

        return self.item_dao.buscar_por_id(item_id)
    
    def get_pedidos_pendentes(self):

        return self.pedido_dao.buscar_pedidos_pendentes()