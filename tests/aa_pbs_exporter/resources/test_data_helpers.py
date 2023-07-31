from pathlib import Path
from typing import Any, Callable, Protocol, Sequence


# TODO Make snippet


class DataForTestingProtocol(Protocol):
    name: str
    description: str
    data: Any


def compare_expected_and_result(
    test_data: Sequence[DataForTestingProtocol],
    expected_results: dict[str, Any],
    results: dict[str, Any],
):
    """Compare two dictionaries.

    Keys are assumed to be the name field from the members of `test_data`.
    """
    test_keys = set((data.name for data in test_data))
    assert len(test_keys) == len(test_data), "Duplicate keys in test_data suspected."
    expected_keys = set(expected_results.keys())
    assert test_keys == expected_keys, "Keys should be the same."
    result_keys = set(results.keys())
    assert test_keys == result_keys, "Keys should be the same."

    for item in test_data:
        assert (
            expected_results[item.name] == results[item.name]
        ), f"{item.name}: {item.description}"


def get_results(
    test_data: Sequence[DataForTestingProtocol],
    result_func: Callable[[DataForTestingProtocol], Any],
    output_path: Path,
) -> dict[str, Any]:
    """
    Generate results, and output to a .py file

    Generate results from data, output the data and result as repr
    to .py files. One file for each result will be generated, as well
    as a file with the collected results.

    The collected results are stored as a dict, with the key being
    the `TestDataProtocol.name` field.

    For best results, ensure that all objects have a usable __repr__


    Args:
        test_data: _description_
        result_func: The function used to generate results from `test_data`
        output_path: Directory to save output files to. Missing directories will
            be created

    Returns:
        The collected results
    """
    collected_results = {}
    for item in test_data:
        result = result_func(item.data)
        individual_outpath = output_path / f"{item.name}.py"
        output_data_and_results_repr(individual_outpath, test_data=item, result=result)
        collected_results[item.name] = result
    collected_outpath = output_path / "collected.py"
    output_data_and_results_repr(
        collected_outpath, test_data=test_data, result=collected_results
    )
    return collected_results


def output_data_and_results_repr(output_path: Path, test_data, result):
    """
    Save the repr of `test_data` and `result` to a file.

    Saves the repr of passed in objects to a file, formatted as python code.

    Example:
        test_data = repr(test_data)

        result_data = repr(result)

    This is to allow easy verification of result, and copypasta compatibility.

    Args:
        output_path: Path to output file. Usually has a `.py` suffix.
        test_data: _description_
        result: _description_
    """
    output_txt = f"test_data = {repr(test_data)}\nresult_data = {repr(result)}"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output_txt)
