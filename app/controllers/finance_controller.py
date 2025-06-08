from fastapi import APIRouter, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database import get_connection, insert_trade_history, insert_asset
from app.upload_csv import process_uploaded_csv
from datetime import datetime

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# --- LIST CURRENT ASSETS ---
@router.get("/assets")
def list_assets(request: Request):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Asset")
    assets = cursor.fetchall()
    cursor.close()
    conn.close()
    return templates.TemplateResponse("index_list.html", {"request": request, "assets": assets})


# --- ADD ASSET FORM ---
@router.get("/assets/add")
def add_asset_form(request: Request):
    return templates.TemplateResponse("index_form.html", {"request": request, "action": "Add", "asset": {}})


# --- ADD NEW ASSET + HISTORY ---
@router.post("/assets/add")
def add_asset(
    name: str = Form(...),
    type: str = Form(...),
    value: float = Form(...)
):
    dt = datetime.now()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT timestamp FROM Asset WHERE name = %s", (name,))
    existing = cursor.fetchone()

    if existing:
        existing_ts = existing[0]
        if dt > existing_ts:
            cursor.execute(
                "UPDATE Asset SET current_price = %s, timestamp = %s WHERE name = %s",
                (value, dt, name)
            )
    else:
        cursor.execute(
            "INSERT INTO Asset (name, type, current_price, timestamp) VALUES (%s, %s, %s, %s)",
            (name, type, value, dt)
        )

    # cursor.execute(
    #     "INSERT INTO TradeHistory (asset_name, type, value, timestamp) VALUES (%s, %s, %s, %s)",
    #     (name, type, dt, value)
    # )
    insert_trade_history(type, name, dt, value)

    conn.commit()
    cursor.close()
    conn.close()
    return RedirectResponse(url="/assets", status_code=303)


# --- EDIT FORM ---
@router.get("/assets/edit/{asset_id}")
def edit_index_form(asset_id: int, request: Request):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Asset WHERE id=%s", (asset_id,))
    asset = cursor.fetchone()
    cursor.close()
    conn.close()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return templates.TemplateResponse("index_form.html", {"request": request, "action": "Edit", "asset": asset})


# --- APPLY EDIT ---
@router.post("/assets/edit/{asset_id}")
def edit_index(
    asset_id: int,
    name: str = Form(...),
    type: str = Form(...),
    value: float = Form(...)
):
    current_ts = datetime.now()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Asset WHERE id=%s", (asset_id,))
    asset = cursor.fetchone()
    if not asset:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Asset not found for editing")

    cursor.execute(
        """
        UPDATE Asset
        SET name = %s,
            type = %s,
            current_price = %s,
            timestamp = %s
        WHERE id = %s
        """,
        (name, type, value, current_ts, asset_id)
    )

    cursor.execute(
        """
        INSERT INTO TradeHistory (asset_name, type, value, timestamp)
        VALUES (%s, %s, %s, %s)
        """,
        (name, type, value, current_ts)
    )

    conn.commit()
    cursor.close()
    conn.close()
    return RedirectResponse(url="/assets", status_code=303)

# --- DELETE ---
@router.get("/assets/delete/{asset_id}")
def delete_index(asset_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Asset WHERE id=%s", (asset_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Asset not found")
    asset_name = row[0]

    # Delete asset and history
    cursor.execute("DELETE FROM TradeHistory WHERE asset_name=%s", (asset_name,))
    cursor.execute("DELETE FROM Asset WHERE id=%s", (asset_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return RedirectResponse(url="/assets", status_code=303)


# --- UPLOAD CSV FORM ---
@router.get("/upload-csv")
def upload_csv_form(request: Request):
    return templates.TemplateResponse("upload_csv.html", {"request": request})


# --- HANDLE CSV UPLOAD ---
@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    await process_uploaded_csv(file)
    return RedirectResponse(url="/assets", status_code=303)
