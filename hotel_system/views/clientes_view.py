import pandas as pd
import streamlit as st

import services.cliente_service as svc


def render_clientes():
    st.title("👥 Clientes")
    st.markdown("---")

    tab_lista, tab_novo, tab_editar = st.tabs(
        ["📋 Lista de Clientes", "➕ Novo Cliente", "✏️ Editar / Excluir"]
    )

    with tab_lista:
        _render_lista()

    with tab_novo:
        _render_form_novo()

    with tab_editar:
        _render_editar()


# ──────────────────────────────────────────────────────────────
# LISTA
# ──────────────────────────────────────────────────────────────

def _render_lista():
    st.subheader("Todos os clientes")

    busca = st.text_input("🔍 Buscar por nome, e-mail ou CPF", placeholder="Ex: João")

    try:
        if busca.strip():
            clientes = svc.pesquisar_clientes(busca)
        else:
            clientes = svc.listar_clientes()
    except Exception as e:
        st.error(f"Erro ao carregar clientes: {e}")
        return

    if not clientes:
        st.info("Nenhum cliente encontrado.")
        return

    df = pd.DataFrame(clientes)[["id", "nome", "email", "telefone", "cpf", "created_at"]]
    df.columns = ["ID", "Nome", "E-mail", "Telefone", "CPF", "Cadastrado em"]
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"{len(clientes)} cliente(s) encontrado(s).")


# ──────────────────────────────────────────────────────────────
# NOVO CLIENTE
# ──────────────────────────────────────────────────────────────

def _render_form_novo():
    st.subheader("Cadastrar novo cliente")

    with st.form("form_novo_cliente", clear_on_submit=True):
        nome = st.text_input("Nome completo *", placeholder="Ex: João Silva Santos")
        col1, col2 = st.columns(2)
        with col1:
            email = st.text_input("E-mail *", placeholder="joao@email.com")
        with col2:
            cpf = st.text_input("CPF *", placeholder="000.000.000-00")
        telefone = st.text_input("Telefone", placeholder="(11) 99999-9999")

        st.markdown("*\\* campos obrigatórios*")
        submit = st.form_submit_button("💾 Cadastrar Cliente", use_container_width=True)

    if submit:
        try:
            svc.criar_cliente(nome=nome, email=email, cpf=cpf, telefone=telefone)
            st.success(f"✅ Cliente **{nome}** cadastrado com sucesso!")
        except ValueError as e:
            st.error(f"❌ {e}")
        except Exception as e:
            st.error(f"❌ Erro inesperado: {e}")


# ──────────────────────────────────────────────────────────────
# EDITAR / EXCLUIR
# ──────────────────────────────────────────────────────────────

def _render_editar():
    st.subheader("Editar ou excluir cliente")

    try:
        clientes = svc.listar_clientes()
    except Exception as e:
        st.error(f"Erro ao carregar clientes: {e}")
        return

    if not clientes:
        st.info("Nenhum cliente cadastrado.")
        return

    opcoes = {c["id"]: f"{c['nome']}  —  CPF: {c['cpf']}" for c in clientes}
    cliente_id = st.selectbox(
        "Selecionar cliente",
        options=list(opcoes.keys()),
        format_func=lambda x: opcoes[x],
    )

    selecionado = next((c for c in clientes if c["id"] == cliente_id), None)
    if not selecionado:
        return

    st.markdown("#### Dados atuais")

    with st.form("form_editar_cliente"):
        nome = st.text_input("Nome completo", value=selecionado["nome"])
        col1, col2 = st.columns(2)
        with col1:
            email = st.text_input("E-mail", value=selecionado["email"])
        with col2:
            cpf = st.text_input("CPF", value=selecionado["cpf"])
        telefone = st.text_input("Telefone", value=selecionado["telefone"])

        col_salvar, col_excluir = st.columns([3, 1])
        with col_salvar:
            salvar = st.form_submit_button("💾 Salvar Alterações", use_container_width=True)
        with col_excluir:
            excluir = st.form_submit_button("🗑️ Excluir", use_container_width=True, type="secondary")

    if salvar:
        try:
            svc.atualizar_cliente(
                cliente_id=cliente_id,
                nome=nome,
                email=email,
                cpf=cpf,
                telefone=telefone,
            )
            st.success("✅ Cliente atualizado com sucesso!")
            st.rerun()
        except ValueError as e:
            st.error(f"❌ {e}")
        except Exception as e:
            st.error(f"❌ Erro inesperado: {e}")

    if excluir:
        try:
            svc.deletar_cliente(cliente_id)
            st.success("✅ Cliente excluído com sucesso!")
            st.rerun()
        except ValueError as e:
            st.warning(f"⚠️ {e}")
        except Exception as e:
            st.error(f"❌ Erro inesperado: {e}")
