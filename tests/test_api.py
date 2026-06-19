from patchwork.services import meaning_service


RAW = "META:: ticket=>A-100 ;; source=>fax ;; region=>north\nWORDS:: raw=>customer says package late and needs rapid lane ;; tone=>angry\nFACTS:: amount=>1450 ;; retry=>yes ;; vip=>no"


def test_transform_returns_structured_payload(client, monkeypatch):
    monkeypatch.setattr(meaning_service.CLIENT, "related_words", lambda term: [])
    response = client.post("/api/v1/transform", json={"raw_text": RAW})
    data = response.json()
    assert response.status_code == 200
    assert data["input"]["meta"]["ticket"] == "A-100"
    assert data["meaning"]["word_swaps"]
    assert data["flags"]["decision_flag"] == "STOP_AND_STARE"


def test_replay_returns_saved_payload(client, monkeypatch):
    monkeypatch.setattr(meaning_service.CLIENT, "related_words", lambda term: [])
    client.post("/api/v1/transform", json={"raw_text": RAW})
    response = client.post("/api/v1/admin/replay", json={"ticket": "A-100"})
    assert response.status_code == 200
    assert response.json()["payload"]["meaning"]["ticket"] == "A-100"


def test_missing_example_comes_back_404(client):
    response = client.get("/api/v1/examples/nope")
    assert response.status_code == 404
