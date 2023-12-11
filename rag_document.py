import re
from pydantic import BaseModel, Field

class RagDocument(BaseModel):
    id: str
    distance: float
    document: str
    metadata: dict

    def __repr__(self) -> str:
        document_wo_nl = re.sub(r'\s+', ' ', self.document).replace('\n', ' ')
        metadata_str = ''.join([f'    {k}: {v}\n' for k, v in self.metadata.items()])
        return (
            f"Document:\n"
            f"  ID: {self.id}\n"
            f"  Distance: {self.distance}\n"
            f"  Document: {document_wo_nl[:100]}...\n"  # Truncate document for brevity
            f"  Metadata:\n"
            f"{metadata_str}\n"
        )
