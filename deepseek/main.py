from flask import Flask, request, jsonify
from modules.deepseek_runner import run_deepseek
from modules.deepseek_filemanager import read_prompt_file
from modules.smart_result_handler import format_results
from modules.deepseek_writer import write_output
from modules.gaurdian import run_safety_checks
import os

app = Flask(__name__)

@app.route('/run_karx', methods=['POST'])
def run_karx():
    try:
        data = request.json
        input_file = data.get('input_file', 'Prompts/new_idea.txt')  # default file
        permissions = data.get('permissions', '')

        # ✅ 1. Run safety check (guardian)
        run_safety_checks(permissions)

        # ✅ 2. Read input
        input_text = read_prompt_file(input_file)

        # ✅ 3. Process with main AI logic
        result = run_deepseek(input_text)

        # ✅ 4. Format output
        formatted_result = format_results(result)

        # ✅ 5. Write to file
        output_file_path = "output/deepseek_output.txt"
        write_output(output_file_path, formatted_result)
        print("output",write_output)

        return jsonify({"status": "success", "result": formatted_result})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
