def test_auth_login(client):
    response = client.post(
        "/auth/login",
        data={"username": "fred", "password": "secret"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    return data["access_token"]

def test_cadastrar_processo(client):
    token = test_auth_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "numero_cnj": "5001234-88.2023.8.13.0024",
        "titulo": "Ação de Cobrança",
        "cliente_nome": "Empresa X",
        "valor_causa": "50000.00",
        "advogado_oab": "MG123456"
    }
    
    response = client.post("/processos/cadastrar", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["numero_cnj"] == payload["numero_cnj"]
    assert "id" in data

def test_consultar_processo(client):
    # Setup: Ensure process exists
    test_cadastrar_processo(client)
    token = test_auth_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    # We assume ID 1 because it's a fresh in-memory DB
    response = client.get("/processos/1", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["numero_cnj"] == "5001234-88.2023.8.13.0024"

def test_unauthorized_access(client):
    response = client.get("/processos/1")
    assert response.status_code == 401
