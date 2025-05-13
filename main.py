from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
from pypdf import PdfReader, PdfWriter
import io

app = FastAPI()

@app.post("/unlock-pdf/")
async def unlock_pdf(file: UploadFile, password: str = Form(...)):
    try:
        # Leer el archivo PDF subido
        pdf_reader = PdfReader(file.file)

        # Intentar descifrar el PDF con la contraseña proporcionada
        if pdf_reader.is_encrypted:
            success = pdf_reader.decrypt(password)
            if success == 0:  # pypdf devuelve 0 si falla
                raise HTTPException(
                    status_code=401,
                    detail="La contraseña es incorrecta. Verifica e intenta de nuevo."
                )

        # Crear un nuevo PDF sin contraseña
        pdf_writer = PdfWriter()
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

        # Guardar el nuevo PDF en memoria
        output_pdf = io.BytesIO()
        pdf_writer.write(output_pdf)
        output_pdf.seek(0)

        # Preparar el nombre del archivo resultante
        original_name = file.filename or "document.pdf"
        unlocked_name = f"unlocked_{original_name}"

        # Devolver el archivo como respuesta
        return StreamingResponse(
            output_pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={unlocked_name}"}
        )

    except Exception as e:
        if isinstance(e, ValueError):
            raise HTTPException(status_code=401, detail="Contraseña incorrecta.")
        raise HTTPException(status_code=500, detail="Error al procesar el PDF.")
