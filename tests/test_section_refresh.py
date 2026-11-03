"""保持否定句完整、限定更新来源、避免向量与正文错位。"""
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from app.rag.document_loader import Document
from learning.pgvector.step_09_section_chunking import build_section_documents, split_by_heading
from learning.pgvector.step_09b_refresh_plan import find_obsolete_chunk_ids
from learning.pgvector.step_09c_refresh_vectors import validate_vectors
from learning.pgvector.step_03_insert_one_chunk import save_one_chunk


class SectionRefreshTests(unittest.TestCase):
    @patch('learning.pgvector.step_03_insert_one_chunk.connect_learning_db')
    @patch('learning.pgvector.step_03_insert_one_chunk.EmbeddingService', return_value=SimpleNamespace(
        model='text-embedding-v2', dimensions=1536))
    def test_same_dimension_but_different_model_never_writes(self, service, connect):
        with self.assertRaises(ValueError):
            save_one_chunk(Document('正文', {'source':'products.md','chunk_id':'one'}))
        connect.assert_not_called()

    def test_heading_chunks_preserve_all_nonempty_lines_and_metadata(self):
        text = '# 商品\n\n## 键盘\n没有标注防水能力。\n\n## 鼠标\n续航约30天。\n'
        source = Document(text, {'source':'products.md'})
        chunks = build_section_documents([source])
        self.assertEqual(len(chunks), 2)
        self.assertIn('没有标注防水能力。', chunks[0].content)
        self.assertNotIn('30天', chunks[0].content)
        self.assertEqual([line for c in chunks for line in c.content.splitlines() if line.strip()],
                         [line for line in text.splitlines() if line.strip()])
        self.assertEqual(source.metadata, {'source':'products.md'})
        self.assertEqual(split_by_heading('  \n'), [])

    def test_refresh_plan_keeps_other_sources_and_valid_ids(self):
        old = [{'source':'products.md','chunk_id':'old'},
               {'source':'shipping.md','chunk_id':'shipping'},
               {'source':'products.md','chunk_id':'keep'}]
        new = [Document('正文',{'source':'products.md','chunk_id':'keep'})]
        self.assertEqual(find_obsolete_chunk_ids(old,new), ['old'])
        self.assertEqual(find_obsolete_chunk_ids(old,[]), [])
        self.assertEqual(len(old), 3)

    def test_invalid_or_misaligned_vectors_are_rejected_before_writes(self):
        chunks=[Document('正文',{'source':'products.md','chunk_id':'one'})]
        for vectors in ([], [[0.1]], [[0.0]*1536], [[float('nan')]*1536]):
            with self.subTest(vectors_count=len(vectors)):
                with self.assertRaises(RuntimeError):
                    validate_vectors(chunks,vectors)
