import main
import scheduler
from unittest.mock import patch
import datetime

def test_cat(cat):
    print(f"\n--- Testing: {cat} ---")
    with patch('scheduler.Scheduler.get_current_task', return_value=(cat, "spotlight", "rank")):
        main.main()

test_cat("featured_tv")
test_cat("hobby")
