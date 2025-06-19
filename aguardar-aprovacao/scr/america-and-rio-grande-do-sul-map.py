import geopandas
import pandas
import matplotlib.pyplot as plt

# ==============================================================================
# 1. Função para Definir os Caminhos dos Arquivos Geoespaciais
# ==============================================================================
def obter_caminhos_arquivos_geospaciais():
    """
    Retorna um dicionário com os caminhos absolutos para os arquivos shapefile necessários.
    ATENÇÃO: Substitua estes caminhos pelos caminhos reais onde seus arquivos estão salvos.
    """
    caminhos_arquivos = {
        'paises_mundo': r"C:\Users\Carlos Henrique\Downloads\ne_10m_admin_0_countries\ne_10m_admin_0_countries.shp",
        'estados_brasil': r"C:\Users\Carlos Henrique\Downloads\BR_UF_2024\BR_UF_2024.shp",
        'regioes_imediatas_brasil': r"C:\Users\Carlos Henrique\Downloads\BR_RG_Imediatas_2024\BR_RG_Imediatas_2024.shp",
        'municipios_brasil': r"C:\Users\Carlos Henrique\Downloads\BR_Municipios_2024 (1)\BR_Municipios_2024.shp"
    }
    return caminhos_arquivos

# ==============================================================================
# 2. Função para Carregar e Filtrar os Dados Geoespaciais
# ==============================================================================
def carregar_e_filtrar_dados_geospaciais(caminhos_arquivos):
    """
    Carrega os shapefiles dos caminhos fornecidos e filtra os dados relevantes,
    especialmente para o Rio Grande do Sul e a América do Sul.

    Args:
        caminhos_arquivos (dict): Dicionário contendo os caminhos para os shapefiles.

    Returns:
        dict: Um dicionário contendo os GeoDataFrames processados e filtrados.
    """
    dados_processados = {
        'america_do_sul_paises': None,
        'dados_estados_brasil': None,
        'dados_regioes_imediatas_brasil': None,
        'dados_municipios_brasil': None,
        'estado_rio_grande_do_sul': None,
        'regioes_imediatas_rio_grande_do_sul': None,
        'municipios_rio_grande_do_sul': None
    }

    codigo_rio_grande_do_sul = 43
    sigla_rio_grande_do_sul = 'RS'

    # Carregamento e filtragem de países
    try:
        dados_geometria_paises_mundo = geopandas.read_file(caminhos_arquivos['paises_mundo'])
        if 'CONTINENT' in dados_geometria_paises_mundo.columns:
            dados_processados['america_do_sul_paises'] = dados_geometria_paises_mundo[
                dados_geometria_paises_mundo['CONTINENT'] == 'South America'
            ].copy()
        else:
            print("AVISO: Coluna 'CONTINENT' não encontrada para filtragem de países. Verifique o GeoDataFrame de países.")
    except Exception as erro:
        print(f"ERRO: Ao carregar ou filtrar dados de países do mundo: {erro}")

    # Carregamento e reprojeção de estados do Brasil
    try:
        dados_geometria_estados_brasil = geopandas.read_file(caminhos_arquivos['estados_brasil'])
        # Garante que o CRS seja o mesmo para plotagem consistente
        if dados_processados['america_do_sul_paises'] is not None and \
           dados_processados['america_do_sul_paises'].crs != dados_geometria_estados_brasil.crs:
            dados_geometria_estados_brasil = dados_geometria_estados_brasil.to_crs(
                dados_processados['america_do_sul_paises'].crs
            )
        dados_processados['dados_estados_brasil'] = dados_geometria_estados_brasil
    except Exception as erro:
        print(f"ERRO: Ao carregar dados dos estados do Brasil: {erro}")

    # Carregamento e reprojeção de regiões imediatas do Brasil
    try:
        dados_geometria_regioes_imediatas_brasil = geopandas.read_file(caminhos_arquivos['regioes_imediatas_brasil'])
        if dados_processados['america_do_sul_paises'] is not None and \
           dados_processados['america_do_sul_paises'].crs != dados_geometria_regioes_imediatas_brasil.crs:
            dados_geometria_regioes_imediatas_brasil = dados_geometria_regioes_imediatas_brasil.to_crs(
                dados_processados['america_do_sul_paises'].crs
            )
        dados_processados['dados_regioes_imediatas_brasil'] = dados_geometria_regioes_imediatas_brasil
    except Exception as erro:
        print(f"ERRO: Ao carregar dados das regiões imediatas do Brasil: {erro}")

    # Carregamento e reprojeção de municípios do Brasil
    try:
        dados_geometria_municipios_brasil = geopandas.read_file(caminhos_arquivos['municipios_brasil'])
        if dados_processados['america_do_sul_paises'] is not None and \
           dados_processados['america_do_sul_paises'].crs != dados_geometria_municipios_brasil.crs:
            dados_geometria_municipios_brasil = dados_geometria_municipios_brasil.to_crs(
                dados_processados['america_do_sul_paises'].crs
            )
        dados_processados['dados_municipios_brasil'] = dados_geometria_municipios_brasil
    except Exception as erro:
        print(f"ERRO: Ao carregar dados dos municípios do Brasil: {erro}")

    # Filtragem de dados específicos do Rio Grande do Sul
    if dados_processados['dados_estados_brasil'] is not None:
        dados_processados['estado_rio_grande_do_sul'] = dados_processados['dados_estados_brasil'][
            (dados_processados['dados_estados_brasil']['CD_UF'] == codigo_rio_grande_do_sul) |
            (dados_processados['dados_estados_brasil']['SIGLA_UF'] == sigla_rio_grande_do_sul)
        ].copy()

    if dados_processados['dados_regioes_imediatas_brasil'] is not None and \
       dados_processados['estado_rio_grande_do_sul'] is not None and \
       not dados_processados['estado_rio_grande_do_sul'].empty:
        dados_processados['regioes_imediatas_rio_grande_do_sul'] = dados_processados['dados_regioes_imediatas_brasil'][
            (dados_processados['dados_regioes_imediatas_brasil']['CD_UF'] == codigo_rio_grande_do_sul) |
            (dados_processados['dados_regioes_imediatas_brasil']['SIGLA_UF'] == sigla_rio_grande_do_sul)
        ].copy()

    if dados_processados['dados_municipios_brasil'] is not None and \
       dados_processados['estado_rio_grande_do_sul'] is not None and \
       not dados_processados['estado_rio_grande_do_sul'].empty:
        dados_processados['municipios_rio_grande_do_sul'] = dados_processados['dados_municipios_brasil'][
            (dados_processados['dados_municipios_brasil']['CD_UF'] == codigo_rio_grande_do_sul) |
            (dados_processados['dados_municipios_brasil']['SIGLA_UF'] == sigla_rio_grande_do_sul)
        ].copy()

    return dados_processados

# ==============================================================================
# 3. Função para Plotar o Mapa Detalhado do Rio Grande do Sul (Eixo Principal)
# ==============================================================================
def plotar_mapa_rs_detalhado(eixos_plotagem, dados_mapa):
    """
    Plota as camadas detalhadas do Rio Grande do Sul (estado, regiões imediatas, municípios)
    no eixo principal fornecido.

    Args:
        eixos_plotagem (matplotlib.axes.Axes): O objeto de eixos onde o mapa será plotado.
        dados_mapa (dict): Dicionário contendo os GeoDataFrames processados.
    """
    estado_rs = dados_mapa.get('estado_rio_grande_do_sul')
    regioes_imediatas_rs = dados_mapa.get('regioes_imediatas_rio_grande_do_sul')
    municipios_rs = dados_mapa.get('municipios_rio_grande_do_sul')

    if estado_rs is not None and not estado_rs.empty:
        estado_rs.plot(ax=eixos_plotagem, color='#FFECB3', edgecolor='#FFC107', linewidth=1.0, zorder=1)

        if regioes_imediatas_rs is not None and not regioes_imediatas_rs.empty:
            regioes_imediatas_rs.plot(ax=eixos_plotagem, color='none', edgecolor='#2196F3', linewidth=0.7, zorder=2)
            # Adicionando rótulos das regiões imediatas
            for indice_linha, linha_dados in regioes_imediatas_rs.iterrows():
                nome_da_regiao = linha_dados['NM_RGI']
                centroide_geometria = linha_dados['geometry'].centroid
                eixos_plotagem.annotate(
                    text=nome_da_regiao,
                    xy=(centroide_geometria.x, centroide_geometria.y),
                    xytext=(3, 3), # Pequeno offset para o texto não ficar exatamente no centro
                    textcoords="offset points",
                    fontsize=8,
                    color='#543005',
                    ha='center', # Alinhamento horizontal do texto
                    va='center'  # Alinhamento vertical do texto
                )

        if municipios_rs is not None and not municipios_rs.empty:
            municipios_rs.plot(ax=eixos_plotagem, color='none', edgecolor='black', linewidth=0.1, zorder=3)
    else:
        print("AVISO: Dados do Rio Grande do Sul não disponíveis para o mapa detalhado.")

    # Ajustar os limites do mapa principal para focar no RS
    if estado_rs is not None and not estado_rs.empty:
        min_x, min_y, max_x, max_y = estado_rs.total_bounds
        margem_estado_rs = 0.1 # Margem em graus para visualizar um pouco do entorno do RS
        eixos_plotagem.set_xlim(min_x - margem_estado_rs, max_x + margem_estado_rs)
        eixos_plotagem.set_ylim(min_y - margem_estado_rs, max_y + margem_estado_rs)

    eixos_plotagem.set_title('Mapa Detalhado do Rio Grande do Sul com Regiões e Municípios', fontsize=16)
    eixos_plotagem.set_axis_off() # Remove os eixos de coordenadas (latitude/longitude)

# ==============================================================================
# 4. Função para Plotar o Mapa da América do Sul (Inset)
# ==============================================================================
def plotar_mapa_america_sul_inset(eixos_plotagem_inset, dados_mapa):
    """
    Plota o mapa da América do Sul com destaque para o Brasil e o Rio Grande do Sul
    no eixo inset fornecido.

    Args:
        eixos_plotagem_inset (matplotlib.axes.Axes): O objeto de eixos para o inset map.
        dados_mapa (dict): Dicionário contendo os GeoDataFrames processados.
    """
    america_sul_paises = dados_mapa.get('america_do_sul_paises')
    estados_brasil = dados_mapa.get('dados_estados_brasil')
    estado_rs = dados_mapa.get('estado_rio_grande_do_sul')

    # Plotar países da América do Sul (fundo mais claro)
    if america_sul_paises is not None and not america_sul_paises.empty:
        america_sul_paises.plot(ax=eixos_plotagem_inset, color='#E0E0E0', edgecolor='white', linewidth=0.2, zorder=1)

        # Plotar as divisões dos estados do Brasil no inset
        if estados_brasil is not None and not estados_brasil.empty:
            estados_brasil.plot(ax=eixos_plotagem_inset, color='none', edgecolor='gray', linewidth=0.1, zorder=2)
            
            # Plota o contorno externo do Brasil (união de todos os estados)
            contorno_do_brasil = estados_brasil.unary_union # Considerar .union_all() para versões futuras
            geopandas.GeoSeries([contorno_do_brasil]).plot(ax=eixos_plotagem_inset, color='none', edgecolor='#4CAF50', linewidth=0.5, zorder=3)

        # Destacar o Rio Grande do Sul no eixo inset (com preenchimento)
        if estado_rs is not None and not estado_rs.empty:
            estado_rs.plot(ax=eixos_plotagem_inset, color='#FFECB3', edgecolor='#FFC107', linewidth=0.5, zorder=4)
    else:
        print("AVISO: Dados da América do Sul não disponíveis para o eixo inset.")

    # Ajustar os limites do eixo inset para focar na América do Sul
    if america_sul_paises is not None and not america_sul_paises.empty:
        min_x_america_sul, min_y_america_sul, max_x_america_sul, max_y_america_sul = america_sul_paises.total_bounds
        margem_america_sul_inset = 2.0 # Margem em graus para o inset
        eixos_plotagem_inset.set_xlim(min_x_america_sul - margem_america_sul_inset, max_x_america_sul + margem_america_sul_inset)
        eixos_plotagem_inset.set_ylim(min_y_america_sul - margem_america_sul_inset, max_y_america_sul + margem_america_sul_inset)
    
    eixos_plotagem_inset.set_axis_off() # Remove os eixos de coordenadas para o inset

# ==============================================================================
# 5. Função Principal para Executar o Processo
# ==============================================================================
def main():
    """
    Função principal que orquestra o carregamento de dados, a plotagem dos mapas
    e o salvamento da figura final.
    """
    print("Iniciando a geração do mapa combinado...")

    # 1. Obter os caminhos dos arquivos
    caminhos_dos_arquivos = obter_caminhos_arquivos_geospaciais()
    print("Caminhos dos arquivos definidos.")

    # 2. Carregar e filtrar os dados geoespaciais
    dados_geoespaciais_processados = carregar_e_filtrar_dados_geospaciais(caminhos_dos_arquivos)
    print("Dados geoespaciais carregados e filtrados.")

    # 3. Criar a figura principal para os mapas
    figura_mapa_combinado = plt.figure(figsize=(12, 12)) # Define o tamanho total da figura

    # 4. Criar o eixo principal para o mapa detalhado do Rio Grande do Sul
    eixo_principal_rs = figura_mapa_combinado.add_axes([0.05, 0.05, 0.9, 0.9]) # [left, bottom, width, height]
    print("Eixo principal para o Rio Grande do Sul criado.")

    # 5. Plotar o mapa detalhado do Rio Grande do Sul no eixo principal
    plotar_mapa_rs_detalhado(eixo_principal_rs, dados_geoespaciais_processados)
    print("Mapa detalhado do Rio Grande do Sul plotado no eixo principal.")

    # 6. Criar o eixo inset para o mapa da América do Sul (contexto)
    # Posição: [x_start, y_start, width, height] em coordenadas normalizadas (0 a 1)
    # Ajustado para o canto inferior esquerdo e um pouco maior
    eixo_inset_america_sul = figura_mapa_combinado.add_axes([0.08, 0.08, 0.35, 0.35])
    print("Eixo inset para a América do Sul criado.")

    # 7. Plotar o mapa da América do Sul no eixo inset
    plotar_mapa_america_sul_inset(eixo_inset_america_sul, dados_geoespaciais_processados)
    print("Mapa da América do Sul plotado no eixo inset.")

    # 8. Salvar a figura combinada
    nome_do_arquivo_final = "mapa-america-e-rio-grande-do-sul.png"
    plt.savefig(nome_do_arquivo_final, dpi=300, bbox_inches='tight') # Salva a figura em alta resolução
    print(f"\nFigura combinada salva como '{nome_do_arquivo_final}'")

    # 9. Exibir a figura (opcional, pode ser removido se só quiser salvar)
    plt.show()

    print("Processo de geração do mapa concluído com sucesso.")

# ==============================================================================
# Ponto de entrada do script
# ==============================================================================
if __name__ == "__main__":
    main()