import json
import os


def load_controls():
  dir_here = os.path.dirname(__file__)
  path = os.path.join(dir_here, 'control_mapping.json')
  with open(path, 'r', encoding='utf-8') as f:
    return json.load(f)


controls = load_controls()


def generate_report(text: str):
  """Generate a structured report from `text`.

  Returns a dict with a summary and a list of findings for consistent output.
  {
    "summary": "Compliance Report",
    "findings": [
      {"rule": <rule_name>, "found": True/False, "keyword": <matched_keyword or None>},
      ...
    ]
  }
  """
  findings = []
  lower_text = text.lower()
  for rule, keywords in controls.items():
    found = False
    matched_keyword = None
    for keyword in keywords:
      if keyword.lower() in lower_text:
        found = True
        matched_keyword = keyword
        break
    findings.append({
      "rule": rule,
      "found": found,
      "keyword": matched_keyword,
    })

  return {"summary": "Compliance Report", "findings": findings}


if __name__ == '__main__':
  import sys

  sample_text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Example text"
  import pprint
  pprint.pprint(generate_report(sample_text))