# Variáveis globais e de teste
SEED_PADRAO = 42
PROB_GERAR_PEDIDO = 0.05  
FATOR_CONSUMO = 1.0

# Margem anti morte da bateria
MARGEM_SEGURANCA = 0.25   

# Custo atribuído a km por cada tipo de veículo
CUSTO_ELET_KM = 0.06 
CUSTO_COMB_KM = 0.30 

# Velocidades de carregamento 
VEL_CARGA_ELET = 100   
VEL_CARGA_COMB = 5000  # Instantâneo !

C02_EMISSAO_COMB_KM = 0.11  # kg CO2 por km para veículos a combustão !
C02_EMISSAO_ELET_KM = 0     # kg CO2 por km para veículos elétricos !

#Duração da simulação em passos
PASSOS_SIMULACAO = 3000   

#Probabilidades de diferentes pedidos
PROB_PREMIUM = 0.20
PROB_ECO_FRIENDLY = 0.10

# Coordenadas do centro e condições para gerar pedidos
HOTSPOT_LAT = 41.1821
HOTSPOT_LON = -8.6891
HOTSPOT_RAIO = 1500  
HOTSPOT_PESO = 8

#Trânsito 
PROB_INICIAR_TRANSITO = 0.0001 
FATOR_TRANSITO_MEDIO = 3.0    
FATOR_TRANSITO_PESADO = 10.0  
DURACAO_TRANSITO = 50        