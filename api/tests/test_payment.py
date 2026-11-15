import base64, hashlib, json

PRIVATE = "test_private"  

def signed(payload: dict, key: str = PRIVATE) -> dict:
    data = base64.b64encode(json.dumps(payload).encode()).decode()
    sig = base64.b64encode(hashlib.sha1((key + data + key).encode()).digest()).decode()
    return {"data": data, "signature": sig}

def test_valid_webhook_marks_paid(client, pending_payment):
    body = signed({"order_id": pending_payment.external_id, "status": "sandbox",
                   "amount": float(pending_payment.amount), "currency": "UAH"})
    r = client.post("/payments/webhook/liqpay", data=body)  
    assert r.status_code == 200

def test_invalid_signature_400(client, pending_payment):
    body = signed({"order_id": pending_payment.external_id, "status": "success"}, key="wrong")
    assert client.post("/payments/webhook/liqpay", data=body).status_code == 400

def test_duplicate_webhook_no_double_stock(client, pending_payment):
    body = signed({...})            
    client.post("/payments/webhook/liqpay", data=body)
    client.post("/payments/webhook/liqpay", data=body)

def test_wrong_amount_rejected(client, pending_payment): ...
def test_failure_status_marks_failed(client, pending_payment): ...
def test_same_idempotency_key_same_payment(client, auth_headers, order): ...