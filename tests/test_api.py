def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_list_jurisdictions(client):
    resp = client.get("/api/jurisdictions/")
    assert resp.status_code == 200
    data = resp.json()
    assert "top_jurisdictions" in data
    assert "all_jurisdictions" in data
    assert len(data["top_jurisdictions"]) == 3
    assert "Delaware" in data["top_jurisdictions"][0]["display_name"]


def test_create_custom_jurisdiction(client):
    resp = client.post(
        "/api/jurisdictions/",
        json={
            "country": "Canada",
            "subdivision": "Ontario",
            "display_name": "Ontario, Canada",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["display_name"] == "Ontario, Canada"
    assert data["is_preset"] is False


def test_create_duplicate_jurisdiction_returns_409(client):
    client.post(
        "/api/jurisdictions/",
        json={"country": "France", "subdivision": None, "display_name": "France"},
    )
    resp = client.post(
        "/api/jurisdictions/",
        json={"country": "France", "subdivision": None, "display_name": "France"},
    )
    assert resp.status_code == 409


def test_create_nda(client, tmp_path, monkeypatch):
    from nda_app import config

    monkeypatch.setattr(config.settings, "output_dir", tmp_path)

    resp = client.post(
        "/api/ndas/",
        json={
            "disclosing_party_name": "Acme Corp",
            "receiving_party_name": "Globex Industries",
            "effective_date": "2026-03-01",
            "term_years": 3,
            "jurisdiction_id": 5,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["disclosing_party_name"] == "Acme Corp"
    assert data["status"] == "draft"
    assert data["expiry_date"] == "2029-03-01"


def test_list_ndas(client, tmp_path, monkeypatch):
    from nda_app import config

    monkeypatch.setattr(config.settings, "output_dir", tmp_path)

    for name in ["Company A", "Company B"]:
        client.post(
            "/api/ndas/",
            json={
                "disclosing_party_name": "Our Corp",
                "receiving_party_name": name,
                "effective_date": "2026-01-01",
            },
        )

    resp = client.get("/api/ndas/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_update_nda_status(client, tmp_path, monkeypatch):
    from nda_app import config

    monkeypatch.setattr(config.settings, "output_dir", tmp_path)

    create_resp = client.post(
        "/api/ndas/",
        json={
            "disclosing_party_name": "Corp X",
            "receiving_party_name": "Corp Y",
            "effective_date": "2026-04-01",
        },
    )
    nda_id = create_resp.json()["id"]

    resp = client.patch(f"/api/ndas/{nda_id}", json={"status": "sent"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "sent"


def test_download_nda(client, tmp_path, monkeypatch):
    from nda_app import config

    monkeypatch.setattr(config.settings, "output_dir", tmp_path)

    create_resp = client.post(
        "/api/ndas/",
        json={
            "disclosing_party_name": "Download Corp",
            "receiving_party_name": "Test Inc",
            "effective_date": "2026-05-01",
        },
    )
    nda_id = create_resp.json()["id"]

    resp = client.get(f"/api/ndas/{nda_id}/download")
    assert resp.status_code == 200
    assert "wordprocessingml" in resp.headers["content-type"]


def test_delete_nda(client, tmp_path, monkeypatch):
    from nda_app import config

    monkeypatch.setattr(config.settings, "output_dir", tmp_path)

    create_resp = client.post(
        "/api/ndas/",
        json={
            "disclosing_party_name": "Delete Corp",
            "receiving_party_name": "Gone Inc",
            "effective_date": "2026-06-01",
        },
    )
    nda_id = create_resp.json()["id"]

    resp = client.delete(f"/api/ndas/{nda_id}")
    assert resp.status_code == 204

    resp = client.get(f"/api/ndas/{nda_id}")
    assert resp.status_code == 404


def test_get_nonexistent_nda_returns_404(client):
    resp = client.get("/api/ndas/9999")
    assert resp.status_code == 404


def test_filter_ndas_by_status(client, tmp_path, monkeypatch):
    from nda_app import config

    monkeypatch.setattr(config.settings, "output_dir", tmp_path)

    create_resp = client.post(
        "/api/ndas/",
        json={
            "disclosing_party_name": "Filter Corp",
            "receiving_party_name": "Status Inc",
            "effective_date": "2026-07-01",
        },
    )
    nda_id = create_resp.json()["id"]
    client.patch(f"/api/ndas/{nda_id}", json={"status": "executed"})

    resp = client.get("/api/ndas/", params={"status": "executed"})
    assert resp.status_code == 200
    assert resp.json()["total"] == 1

    resp = client.get("/api/ndas/", params={"status": "draft"})
    assert resp.status_code == 200
    assert resp.json()["total"] == 0
