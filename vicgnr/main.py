from __future__ import annotations

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from .extensions import db
from .generator import gen_kit_items
from .models import VictimItem, VictimKit

bp = Blueprint("main", __name__)


def _n(x, d=0):
    try:
        v = int(x)
        if v < 0:
            return 0
        return v
    except (TypeError, ValueError):
        return d


def _k(kid):
    z = VictimKit.query.get_or_404(kid)
    if z.user_id != current_user.id:
        abort(403)
    return z


@bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("index.html")


@bp.route("/dashboard")
@login_required
def dashboard():
    a = (
        VictimKit.query.filter_by(user_id=current_user.id)
        .order_by(VictimKit.created_at.desc())
        .all()
    )
    return render_template("dashboard.html", kits=a)


@bp.route("/kits/new", methods=["GET", "POST"])
@login_required
def new_kit():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            title = "kit"
        rl = _n(request.form.get("real_letters"), 6)
        fl = _n(request.form.get("false_letters"), 3)
        rv = _n(request.form.get("real_visual"), 3)
        fv = _n(request.form.get("false_visual"), 2)
        lvl = _n(request.form.get("difficulty"), 3)
        lvl = max(1, min(5, lvl))

        if rl + fl + rv + fv <= 0:
            flash("Add at least one victim.", "error")
            return render_template("new_kit.html")

        kk = VictimKit(
            user_id=current_user.id,
            title=title,
            difficulty=lvl,
            real_letter_count=rl,
            false_letter_count=fl,
            real_visual_count=rv,
            false_visual_count=fv,
        )
        db.session.add(kk)
        db.session.flush()

        arr = gen_kit_items(rl, fl, rv, fv, lvl)

        for q in arr:
            it = VictimItem(
                kit_id=kk.id,
                position=q["position"],
                item_type=q["item_type"],
                is_real=q["is_real"],
                value_sum=q["value_sum"],
                status=q["status"],
            )
            it.set_data(q["payload"])
            db.session.add(it)

        db.session.commit()
        flash("Victim kit generated.", "success")
        return redirect(url_for("main.kit_detail", kit_id=kk.id))

    return render_template("new_kit.html")


@bp.route("/kits/<int:kit_id>")
@login_required
def kit_detail(kit_id: int):
    kit = _k(kit_id)
    return render_template("kit_detail.html", kit=kit)


@bp.route("/kits/<int:kit_id>/pdf")
@login_required
def download_kit_pdf(kit_id: int):
    _ = _k(kit_id)
    flash("PDF later. File for pdf was removed.", "error")
    return redirect(url_for("main.kit_detail", kit_id=kit_id))
