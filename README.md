# 🤖 Qubot

An autonomous exploratory testing library for Python.

### About

Qubot was created out of inspiration to create a fully autonomous testing bot to mimic a real-life
QA-tester.

See [the Qubot paper](docs/qubot_paper.pdf) to learn more about the design decisions and the Q-learning approach behind
this repository. Moreover, see [experiments.ipynb](tests/experiments.ipynb) for the experiment
mentioned in paper.

Hours of painstaking work have been put into this project thus far, and we hope this
library finds actual use in the field of autonomous software testing.

### Getting Started

To get started with Qubot, simply download the library into your project's repository from PyPi:
```
pip install qubot
```

This will download all necessary dependencies, as well as install the `qubot` command line program
in your current Python environment.

#### Run Programmatically

You can specify each aspect of your test programmatically, and run it all within the same code file.

```
from qubot import Qubot, QubotConfigTerminalInfo, QubotConfigModelParameters, QubotDriverParameters, QubotPresetRewardFunc

qb = Qubot(
    url_to_test="https://upmed-starmen.web.app/",
    terminal_info_testing=QubotConfigTerminalInfo(
        terminal_ids=[],
        terminal_classes=["SignIn_login_hcp__qYuvP"],
        terminal_contains_text=[],
    ),
    terminal_info_training=QubotConfigTerminalInfo(
        terminal_ids=[],
        terminal_classes=[],
        terminal_contains_text=["Log in as a Healthcare Provider"],
    ),
    driver_params=QubotDriverParameters(
        use_cache=False,
        max_urls=10,
    ),
    model_params=QubotConfigModelParameters(
        alpha=0.5,
        gamma=0.6,
        epsilon=1,
        decay=0.01,
        train_episodes=1000,
        test_episodes=100,
        step_limit=100,
    ),
    reward_func=QubotPresetRewardFunc.ENCOURAGE_EXPLORATION,
    input_values={
        "color": "#000000",
        "date": "2021-01-01",
        "datetime-local": "2021-01-01T01:00",
        "email": "johndoe@gmail.com",
        "month": "2021-01",
        "number": "1",
        "password": "p@ssw0rd",
        "search": "query",
        "tel": "123-456-7890",
        "text": "text",
        "time":  "00:00:00.00",
        "url": "https://www.google.com/",
        "week": "2021-W01"
    }
)
qb.run()
print(qb.get_stats())
```

See the source code for descriptions of each configuration property. If you'd like to stick with
default values, your `Qubot` instantiation may look as short as the following:
```
qb = Qubot(
    url_to_test="https://upmed-starmen.web.app/",
    QubotConfigTerminalInfo(
        terminal_ids=[],
        terminal_classes=["SignIn_login_hcp__qYuvP"],
        terminal_contains_text=[],
    )
)
```

#### Run Programmatically via a Configuration File

Shorten the Qubot setup code by adding a Qubot configuration `JSON` file in the same directory, as follows:

##### qu_config.json
```
{
	"url": "https://upmed-starmen.web.app/",
	"terminal_info": {
		"training": {
            "ids": [],
            "classes": [
                "SignIn_login_hcp__qYuvP"
            ],
            "contains_text": []
		},
		"testing": {
            "ids": [],
            "classes": [],
            "contains_text": [
                "Log in as a Healthcare Provider"
            ]
		}
	},
	"driver_parameters": {
	    "use_cache": false,
	    "max_urls": 1
	},
	"model_parameters": {
		"alpha": 0.5,
		"gamma": 0.6,
		"epsilon": 1,
		"decay": 0.01,
		"train_episodes": 1000,
		"test_episodes": 100,
		"step_limit": 100
	},
	"reward_func": 3,
	"input_values": {
        "color": "#000000",
        "date": "2021-01-01",
        "datetime-local": "2021-01-01T01:00",
        "email": "johndoe@gmail.com",
        "month": "2021-01",
        "number": "1",
        "password": "p@ssw0rd",
        "search": "query",
        "tel": "123-456-7890",
        "text": "text",
        "time":  "00:00:00.00",
        "url": "https://www.google.com/",
        "week": "2021-W01"
	}
}
```

Then, run the following code to set up and execute the Qubot tests.

##### main.py
```
from qubot import Qubot

qb = Qubot.from_file('./qu_config.json')
qb.run()
print(qb.get_stats())
```

#### Run in Command-Line via a Configuration File

Qubot is automatically installed to your command line when you run `pip install qubot`.

Assuming you've defined the configuration in `./qu_config.json`, enter the
following into your command line to run a test:
```
qubot ./qu_config.json
```

The above will generate an output file called `qu_stats.json` in the same directory. To change
the name of this output file, you can add the `--output_file`/`-o` flag:
```
qubot ./qu_config.json -o output_stats.json
```

See this usage statement for more info on the command line utility:
```
usage: qubot [-h] config_file [--output_file OUTPUT_FILE]
```

#### Retrieving Test Statistics

What good is a testing suite without stats?

To retrieve output statistics on your latest test run in code, simply call `Qubot(...).get_stats()` This is
exemplified above.

Meanwhile, output statistics will be written to a file (default: `qu_stats.json`) if using the command line program.

Statistics have no defined shape, but generally look like the following:
```
{
    "elements_encountered": {
        "count": 80,
        "events": [
            "<html id=\"\" class=\"\"> (bccad3ad-f444-c74a-a440-631241a8dfc3)",
            "<head id=\"\" class=\"\"> (12bf4d04-00df-2541-8b82-1476d4467471)",
            "<meta id=\"\" class=\"\"> (768ecfcb-5f5d-6945-96a6-6a8e6884d8a9)",
            "<link id=\"\" class=\"\"> (34f6f1d4-7b65-5f4b-b92c-fa5ec96e480d)",
            ...
        ]
    },
    "elements_left_clicked": {
        "count": 7,
        "events": [
            "<a id=\"\" class=\"text-left pt-2 pb-2\"> (ad1272a9-2a5a-2844-b741-39a7fbaf6aff)",
            ...
        ]
    },
    "step_count": 110000,
    "reward_sum": -1100000,
    "training_rewards": {
        "count": 1000,
        "events": [
            -1000,
            -2000,
            ...
        ]
    },
    "epsilon_history": {
        "count": 1000,
        "events": [
            1.0,
            0.9901493354116764,
            0.9803966865736877,
            ...
        ]
    },
    "testing_rewards": {
        "count": 100,
        "events": [
            -1000,
            ...
        ]
    },
    "testing_penalties": {
        "count": 100,
        "events": [
            100,
            ...
        ]
    }
}
```

### Authors

<b>Anthony Krivonos</b> <br/>
[Portfolio](https://anthonykrivonos.com) | [GitHub](https://github.com/anthonykrivonos)

<b>Kenneth Chuen</b> <br/>
[GitHub](https://github.com/kenkenchuen)

Created for the [COMSE6156 - Topics in Software Engineering](https://www.coursicle.com/columbia/courses/COMS/E6156/)
course at Columbia University in Spring 2021.
