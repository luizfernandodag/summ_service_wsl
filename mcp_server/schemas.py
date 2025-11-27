from pydantic import BaseModel, Field

# Schema de Entrada (Input) para a ferramenta
class SummarizeTextInput(BaseModel):
    """Schema para a entrada da função summarize_text."""
    text: str = Field(..., description="O texto longo que precisa ser resumido.")

# Schema de Saída (Output) para a ferramenta
class SummarizeTextOutput(BaseModel):
    """Schema para a saída da função summarize_text."""
    summary: str = Field(..., description="O resumo conciso e coerente do texto.")