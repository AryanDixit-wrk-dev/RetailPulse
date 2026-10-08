from db.pipeline_runs import calculate_file_hash


def test_calculate_file_hash_is_deterministic(tmp_path):
    file_path = tmp_path / "sample.csv"

    file_path.write_text(
        "order_id,product\n1001,Laptop\n",
        encoding="utf-8",
    )

    first_hash = calculate_file_hash(str(file_path))
    second_hash = calculate_file_hash(str(file_path))

    assert first_hash == second_hash
    assert len(first_hash) == 64


def test_different_files_have_different_hashes(tmp_path):
    file_one = tmp_path / "one.csv"
    file_two = tmp_path / "two.csv"

    file_one.write_text("data-one", encoding="utf-8")
    file_two.write_text("data-two", encoding="utf-8")

    assert calculate_file_hash(str(file_one)) != calculate_file_hash(
        str(file_two)
    )
