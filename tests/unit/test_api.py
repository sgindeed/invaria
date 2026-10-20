from invaria import Invaria

def test_basic_compression():
    compiler = Invaria(mode="invariant")
    text = "This   is  a test.    This is only a test."
    
    result = compiler.compress(text)
    
    assert result.proof.verified is True
    # The lexical compressor should have cleaned up spaces
    assert result.text == "This is a test. This is only a test."
    assert result.compressed_tokens < result.original_tokens

def test_compile_api():
    compiler = Invaria()
    text = "PostgreSQL is a great database."
    ir = compiler.compile(text)
    
    # Should have extracted some naive entities (e.g., PostgreSQL)
    assert len(ir.nodes) > 0
    found_pg = any(node.value == "PostgreSQL" for node in ir.nodes.values())
    assert found_pg is True
