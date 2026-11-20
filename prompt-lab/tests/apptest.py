import sys; sys.path.insert(0, ".")
from streamlit.testing.v1 import AppTest
at = AppTest.from_file("../app.py", default_timeout=60).run()
print("exceptions:", [e.value for e in at.exception])
print("tabs:", len(at.tabs), "buttons:", [b.label for b in at.button][:12])
