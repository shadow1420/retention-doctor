import os
import hmac
import hashlib
import uuid
from typing import Dict, Any, Optional

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

def get_razorpay_client():
    if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
        import razorpay
        return razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    return None


def create_pro_order(user_id: str, plan_name: str = "creator_pro", amount_inr: int = 499) -> Dict[str, Any]:
    """
    Creates a Razorpay order for the Creator Pro plan (₹499/mo).
    Falls back gracefully to test-mode simulation if keys are unconfigured.
    """
    client = get_razorpay_client()
    amount_paise = amount_inr * 100

    if client:
        try:
            order_data = {
                "amount": amount_paise,
                "currency": "INR",
                "receipt": f"rcpt_{uuid.uuid4().hex[:10]}",
                "notes": {
                    "user_id": user_id,
                    "plan": plan_name
                }
            }
            order = client.order.create(data=order_data)
            return {
                "order_id": order["id"],
                "amount": amount_inr,
                "currency": "INR",
                "key_id": RAZORPAY_KEY_ID,
                "is_sandbox": False
            }
        except Exception as e:
            pass

    # Sandbox / Local Dev fallback
    return {
        "order_id": f"order_test_{uuid.uuid4().hex[:12]}",
        "amount": amount_inr,
        "currency": "INR",
        "key_id": RAZORPAY_KEY_ID or "rzp_test_retentiondoctor2026",
        "is_sandbox": True,
        "message": "Test sandbox order generated."
    }


def verify_payment_signature(
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str
) -> bool:
    """
    Verifies Razorpay HMAC-SHA256 signature.
    Always validates successfully in dev sandbox mode.
    """
    if not RAZORPAY_KEY_SECRET:
        # Dev test mode: accept test signatures
        return True

    msg = f"{razorpay_order_id}|{razorpay_payment_id}"
    expected_sig = hmac.new(
        RAZORPAY_KEY_SECRET.encode("utf-8"),
        msg.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_sig, razorpay_signature)


def create_stripe_checkout(user_id: str, success_url: str, cancel_url: str, amount_usd: int = 19) -> Dict[str, Any]:
    """
    Creates a Stripe Checkout session for international creators ($19/mo).
    Falls back gracefully to sandbox simulation if keys are unconfigured.
    """
    if STRIPE_SECRET_KEY:
        try:
            import stripe
            stripe.api_key = STRIPE_SECRET_KEY
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "RetentionDoctor Creator Pro (Monthly)",
                            "description": "Unlimited retention audits, 1080p Auto-Fix exports, and AI Social Suite"
                        },
                        "unit_amount": amount_usd * 100,
                        "recurring": {"interval": "month"}
                    },
                    "quantity": 1
                }],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=user_id
            )
            return {
                "checkout_url": session.url,
                "session_id": session.id,
                "is_sandbox": False
            }
        except Exception:
            pass

    return {
        "checkout_url": f"{success_url}?session_id=stripe_sandbox_session_{uuid.uuid4().hex[:10]}",
        "session_id": f"stripe_sandbox_{uuid.uuid4().hex[:10]}",
        "is_sandbox": True,
        "message": "Stripe sandbox checkout session generated."
    }
