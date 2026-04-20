from __future__ import annotations

import json
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db

RESCUE_KITS_BY_STATUS = {
    "harmed": 2,
    "stable": 1,
    "unharmed": 0,
}

LETTER_KITS_BY_SYMBOL = {
    "\u03A6": 2,  # Phi
    "\u03A8": 1,  # Psi
    "\u03A9": 0,  # Omega
    "О¦": 2,      # legacy
    "ОЁ": 1,      # legacy
    "О©": 0,      # legacy
}


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    kits = db.relationship("VictimKit", back_populates="user", cascade="all, delete-orphan")

    def set_pass(self, p):
        self.password_hash = generate_password_hash(p)

    def check_pass(self, p):
        return check_password_hash(self.password_hash, p)

    def set_password(self, password):
        self.set_pass(password)

    def check_password(self, password):
        return self.check_pass(password)


class VictimKit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    difficulty = db.Column(db.Integer, nullable=False, default=3)
    real_letter_count = db.Column(db.Integer, nullable=False, default=0)
    false_letter_count = db.Column(db.Integer, nullable=False, default=0)
    real_visual_count = db.Column(db.Integer, nullable=False, default=0)
    false_visual_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="kits")
    items = db.relationship(
        "VictimItem",
        back_populates="kit",
        cascade="all, delete-orphan",
        order_by="VictimItem.position",
    )

    @property
    def rescues_count(self):
        if self.items:
            return sum(item.rescue_kits_count for item in self.items)
        return 0


class VictimItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kit_id = db.Column(db.Integer, db.ForeignKey("victim_kit.id"), nullable=False, index=True)
    position = db.Column(db.Integer, nullable=False)
    item_type = db.Column(db.String(16), nullable=False)  # letter | visual
    is_real = db.Column(db.Boolean, nullable=False, default=True)
    content = db.Column(db.Text, nullable=False)
    value_sum = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(24), nullable=True)

    kit = db.relationship("VictimKit", back_populates="items")

    def set_data(self, x):
        self.content = json.dumps(x, ensure_ascii=True)

    @property
    def data(self):
        return json.loads(self.content)


    def set_payload(self, payload):
        self.set_data(payload)

    @property
    def payload(self):
        return self.data

    @property
    def rescue_kits_count(self):
        if not self.is_real:
            return 0

        by_status = RESCUE_KITS_BY_STATUS.get(self.status or "")
        if by_status is not None:
            return by_status

        payload = self.data
        if isinstance(payload, dict):
            v = payload.get("rescue_kits_count")
            if isinstance(v, int) and v >= 0:
                return v

            if self.item_type == "letter":
                return LETTER_KITS_BY_SYMBOL.get(payload.get("letter"), 0)

        if self.item_type == "visual" and self.value_sum in (0, 1, 2):
            return self.value_sum

        return 0
