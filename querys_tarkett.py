from config import  get_engine
from config import LogEstoqueFornecedor
from functools import wraps
from sqlalchemy import text, insert
from datetime import datetime


def select_produtos_hausz_mapa(*args, **kwargs):
    engine = get_engine()
    with engine.begin() as conn:
        query_produto = (text("""
            SELECT TOP(1) psaldo.Quantidade,pbasico.IdProduto
            ,CONVERT(VARCHAR, psaldo.DataAtualizado, 23) as datas
            ,pprazof.PrazoOperacional,pmarca.Marca,pbasico.[IdProduto]
            ,pbasico.[SKU],pbasico.[NomeProduto]
            ,pbasico.[EstoqueAtual],pbasico.[SaldoAtual] ,pbasico.[IdMarca]
            FROM [HauszMapa].[Produtos].[ProdutoBasico] AS pbasico
            JOIN [HauszMapa].[Produtos].[Marca] AS pmarca
            ON pmarca.IdMarca = pbasico.IdMarca
            JOIN  [HauszMapa].[Produtos].[ProdutoPrazoProducFornec] as pprazof
            ON pprazof.SKU = pbasico.SKU
            JOIN [HauszMapa].[Produtos].[ProdutosSaldos] AS psaldo
            ON psaldo.SKU = pbasico.SKU
            WHERE pbasico.SKU = '{}'""".format(kwargs['SKU'])))

        execquery = conn.execute(query_produto).all()
        try:
            for produtos in execquery:
                produtos_dict = {
                    'SKU':produtos['SKU'],
                    'SALDOANTERIOR':produtos['Quantidade'],
                    'PRAZOANTERIOR':produtos['PrazoOperacional'],
                    'IDMARCA':produtos['IdMarca'],
                    'IDPRODUTO':produtos['IdProduto']}

            yield produtos_dict
        except:
            print("erro query")


def call_procedure_saldo_hausz_mapa(f):
    @wraps(f)
    def update_saldo(*args, **kwargs):
        print('saldoooo Calling decorated function',kwargs.get('sku'), kwargs.get('saldo'))
       
        try:
            print('Calling procedure update SALDO', kwargs)
            engine = get_engine()
            with engine.begin() as conn:

                exec = (text(
                    """EXEC Estoque.SP_AtualizaEstoqueFornecedor @Quantidade = {}, @CodigoProduto = '{}', @IdMarca = {}""".format(
                        kwargs.get('saldo'), kwargs.get('sku'), kwargs.get('idmarca'))))
                exec_produtos = conn.execute(exec)
                print(kwargs.get('sku'), kwargs.get('saldo'))

        except:
            print('erro')
        
 
        return f(*args, **kwargs)
    return update_saldo


@call_procedure_saldo_hausz_mapa
def insert_log_produtos_saldos(*args, **kwargs):
    data = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
    """Recebe parametros de entrada e cadastra log saldo"""
    print('log saldo',kwargs,kwargs.get('sku'), kwargs.get('saldo'))
    engine = get_engine()
    with engine.connect() as conn:
        stmt = (
            insert(LogEstoqueFornecedor).
            values(IdUsuario=1,SKU=kwargs.get('prazoanterior'), IdMarca=kwargs.get('idmarca'),IdTipo=12,
            PrazoProducaoAlterado=kwargs.get('prazo'),ValorAnterio = kwargs.get('saldoanterior')
            ,PrazoProducaoAnterior=kwargs.get('prazoanterior'),DataAlteracao= data, ValorAlterado = kwargs.get('saldo'))
            )
        exec_produtos = conn.execute(stmt)


def call_procedure_prazo_hausz_mapa(f):
    @wraps(f)
    def update_prazo(*args, **kwargs):
        
        print('prazo Calling decorated function', kwargs.get('sku'), kwargs.get('prazo'))

        print('Calling procedure update PRAZO', kwargs)
        engine = get_engine()
        try:
            with engine.begin() as conn:

                exec = (text("""EXEC Estoque.SP_AtualizaPrazoProducao @Sku = '{}' ,@PrazoProducao = {}, @PrazoEstoqueFabrica """.format(
                    str(kwargs.get('sku')), float(kwargs.get('prazo')), int(kwargs.get('idmarca')))))

                exec_produtos = conn.execute(exec)
                print("call procedure prazos - hausz_mapa_update_prazo", kwargs)
        except:
            print("erro prazo")
            return f(*args, **kwargs)
 
    return update_prazo

@call_procedure_prazo_hausz_mapa
def insert_log_produtos_prazos(*args, **kwargs):

    data = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
    """Recebe parametros de entrada e cadastra log prazo"""
    print('log prazoproduto',kwargs.get('sku'), kwargs.get('prazo'))

    engine = get_engine()
    with engine.begin() as conn:

        stmt = (
            insert(LogEstoqueFornecedor).
            values(IdUsuario=1,SKU=kwargs.get('sku'), IdMarca=kwargs.get('idmarca'),IdTipo=12,
            PrazoProducaoAlterado=kwargs.get('prazo'),ValorAnterio=kwargs.get('saldo')
            ,PrazoProducaoAnterior=kwargs.get('prazoanterior'),DataAlteracao= data)
            )
        exec_produtos = conn.execute(stmt)
    
