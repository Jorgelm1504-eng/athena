import streamlit as st
import pandas as pd
import os

# Configuração da página
st.set_page_config(
    page_title="Sistema de Acesso",
    page_icon="🔐",
    layout="centered"
)

# Senha fixa (você pode alterar aqui)
SENHA_CORRETA = "athen@25"

def carregar_csv():
    """Função para carregar dados do CSV"""
    try:
        # Opção 1: Carregar arquivo específico
        # Substitua 'dados.csv' pelo nome do seu arquivo
        if os.path.exists('dados.csv'):
            df = pd.read_csv('dados.csv')
            return df
        else:
            return None
    except Exception as e:
        st.error(f"Erro ao carregar CSV: {e}")
        return None

def processar_dataframe(df):
    """Processa o DataFrame para criar links clicáveis"""
    df_clean = df.copy()
    df_clean.columns = df_clean.columns.str.strip()  # Remove espaços dos nomes das colunas
    
    # Criar links clicáveis na coluna 'link' usando valores da coluna 'ip'
    if 'link' in df_clean.columns and 'ip' in df_clean.columns:
        def criar_url_completa(row):
            ip_value = str(row['ip']).strip()
            if pd.isna(row['ip']) or ip_value == '' or ip_value.lower() in ['temp', 'n/a', 'null']:
                return "N/A"
            
            # Adicionar http:// se não tiver protocolo
            if not ip_value.startswith(('http://', 'https://')):
                return f"http://{ip_value}"
            else:
                return ip_value
        
        # Aplicar as URLs na coluna 'link'
        df_clean['link'] = df_clean.apply(criar_url_completa, axis=1)
    
    return df_clean

col1, col2, col3= st.columns([3, 10, 2])
col4, col5, col6 = st.columns([4, 10, 1])
col7, col7, col9 = st.columns([3, 10, 3])

def tela_login():
    with col2:   
        #"""Tela de login/senha""" 
        st.image ("athenalogo.png")

    with col5:
        st.subheader("&nbsp;" * 4 + "🔐 Acesso as Câmeras")
        
    with col7:
        # Campo de senha
        senha_digitada = st.text_input(
        "Digite a senha:",
        type="password",
        placeholder="Insira sua senha aqui"
    )
    
        # Botão de login
        if st.button("Entrar", type="primary"):
            if senha_digitada == SENHA_CORRETA:
                st.session_state.autenticado = True
                st.success("✅ Senha correta! Redirecionando...")
                st.rerun()
            else:
                st.error("❌ Senha incorreta. Tente novamente.")

        st.markdown("<h6 style='text-align: right; color: gray; font-style: italic;'>by Metrics - IA e Automações</h6>", unsafe_allow_html=True)

def tela_principal():
    """Tela principal após login"""
    st.title("📋 Lista de Câmeras")
    st.markdown("---")
    
    # Botão de logout no sidebar
    with st.sidebar:
        st.write("### Menu")
        if st.button("🚪 Sair"):
            st.session_state.autenticado = False
            st.rerun()
    
    # Carregar dados do CSV
    df = carregar_csv()
    
    if df is not None:
        st.success(f"✅ Dados carregados com sucesso! Total de câmeras: {len(df)}")
        
        # Mostrar informações básicas
        #st.write("### 📊 Resumo das câmeras:")
        #col1, col2, col3 = st.columns(3)
       # with col1:
        #    st.metric("Total de câmeras", len(df))
       # with col2:
        #    st.metric("Total de colunas", len(df.columns))
       # with col3:
           # st.metric("Campos", ", ".join(df.columns[:2]) + ("..." if len(df.columns) > 2 else ""))
        
        st.markdown("---")
        
        # Opções de visualização
        st.write("### 👁️ Visualizar câmeras:")
        
        # Checkbox para mostrar todas as linhas
        mostrar_todos = st.checkbox("Mostrar todas as câmeras")
        
        # Processar DataFrame
        df_processed = processar_dataframe(df)
        
        if mostrar_todos:
            df_display = df_processed
        else:
            # Mostrar apenas primeiras linhas por padrão
            num_linhas = st.slider("Quantas câmeras mostrar?", 1, min(50, len(df_processed)), 10)
            df_display = df_processed.head(num_linhas)
        
        # Informar sobre os links
       # if 'link' in df_display.columns and 'ip' in df_display.columns:
        
        # Mostrar APENAS uma tabela Streamlit
        st.dataframe(
            df_display,
            use_container_width=True,
            column_config={
                "link": st.column_config.LinkColumn(
                    "Link",
                    help="Clique para acessar a câmera"
                )
            } if 'link' in df_display.columns else None
        )
        
        # Opção para download
        st.markdown("---")
        st.write("### 💾 Download:")
        csv_download = df_display.to_csv(index=False)
        st.download_button(
            label="📥 Baixar lista como CSV",
            data=csv_download,
            file_name="cameras_exportadas.csv",
            mime="text/csv"
        )
        
    else:
        # Se não encontrou o CSV, mostrar opções
        st.warning("⚠️ Arquivo CSV não encontrado!")
        
        st.write("### 📁 Opções para carregar dados:")
        
        # Opção 1: Upload de arquivo
        st.write("**Opção 1:** Faça upload do seu arquivo CSV:")
        arquivo_upload = st.file_uploader(
            "Escolha um arquivo CSV",
            type=['csv'],
            help="Selecione o arquivo CSV com a lista de câmeras"
        )
        
        if arquivo_upload is not None:
            try:
                df_upload = pd.read_csv(arquivo_upload)
                st.success("✅ Arquivo carregado com sucesso!")
                
                # Processar o arquivo carregado
                df_upload_processed = processar_dataframe(df_upload)
                
                st.dataframe(
                    df_upload_processed,
                    use_container_width=True,
                    column_config={
                        "link": st.column_config.LinkColumn(
                            "Link",
                            help="Clique para acessar a câmera"
                        )
                    } if 'link' in df_upload_processed.columns else None
                )
            except Exception as e:
                st.error(f"Erro ao ler arquivo: {e}")
        
        # Opção 2: Instruções para arquivo local
        st.write("**Opção 2:** Coloque seu arquivo CSV na mesma pasta do programa:")
        st.info("📝 Renomeie seu arquivo para `dados.csv` e coloque na mesma pasta deste programa Python.")

# Inicializar estado da sessão
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# Controle de fluxo principal
def main():
    if not st.session_state.autenticado:
        tela_login()
    else:
        tela_principal()

if __name__ == "__main__":
    main()