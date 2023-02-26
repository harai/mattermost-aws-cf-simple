import aws_cdk as cdk


def from_file(path: str, params: dict[str, str] = {}) -> str:
  with open(path) as f:
    s = f.read()

  if len(params) == 0:
    return s

  return cdk.Fn.sub(s, params)
