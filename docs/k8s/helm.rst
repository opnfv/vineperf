.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) Anuket, Spirent, AT&T, Ixia  and others.

.. Anuket ViNePerf Documentation master file.

============================================================
Automated deployment of helm charts with python
============================================================

********************
Directory Structure
********************
.. code-block:: console


    ├── charts
    │   ├── mynet.yaml
    │   ├── pod.yaml
    │   ├── proxchart
    │   │   ├── Chart.yaml
    │   │   ├── templates
    │   │   │   ├── daemonset.yaml
    │   │   │   ├── deployment.yaml
    │   │   │   └── service.yaml
    │   │   └── values.yaml
    │   ├── testpmdchart
    │   │   ├── Chart.yaml
    │   │   ├── templates
    │   │   │   ├── daemonset.yaml
    │   │   │   ├── deployment.yaml
    │   │   │   └── service.yaml
    │   │   └── values.yaml
    │   └── trexchart
    │       ├── Chart.yaml
    │       ├── templates
    │       │   ├── daemonset.yaml
    │       │   ├── deployment.yaml
    │       │   └── service.yaml
    │       └── values.yaml
    └── pyscript
        ├── Pipfile
        ├── Pipfile.lock
        └── main.py


***************
Using the tool
***************

Charts folder contains three different charts - ``proxchart, testpmd chart and trex chart``. Any of the one can be used for testing.
Pyscript folder contains ``main.py`` - the main python script that depploys the helm chart of user's choice and returns important configuration of the charts, such as PodIP, Cluster IP, Interface IPs etc.

************************
Important Configurations
************************

In order to run the python script, we need to install Pipenv to create virtual environment. 

Steps:

1. Install

.. code-block:: console

    pip install --user pipenv

2. To activate the environment

.. code-block:: console

    pipenv shell

The last command will automatically read Pipfile.lock and will create an virtual environment.

Once this configuration is done. We can move on to run our python script.

*************************************************
Procedure to automatically deploy the helm chart
*************************************************

Steps:

1. After activating your virtual environment, run the ``main.py``.

.. code-block:: console

    python main.python

2. Enter the location of the chart you want to deploy.

For example, lets deploy proxchart

.. code-block:: console

    Enter the location of helm chart: ../charts/proxchart

3. The last command will execute the entire ``main.py`` and will return all the required information about the chart.

*******
Output
*******

.. code-block:: console

    Status of helm charts

    NAME     	NAMESPACE	REVISION	UPDATED                             	STATUS  	CHART          	APP VERSION
    proxchart	default  	1       	2021-09-27 13:22:21.864816 +0530 IST	deployed	proxchart-0.1.0	1.0
    ----------------------------------------------------------------------------------------------------

    POD DETAILS

    ┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳
    ┃ POD NAME              ┃ NAMESPACE ┃ HOST-IP      ┃ PHASE   ┃ POD-IP     ┃ POD-IPs                ┃
    ┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
    │ prox-6db7c6dc9b-l42v4 │ default   │ 192.168.49.2 │ Running │ 172.17.0.4 │ [{'ip': '172.17.0.4'}] │ 
    └───────────────────────┴───────────┴──────────────┴─────────┴────────────┴────────────────────────┴
    ┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃ POD NAME              ┃ INTERFACE IPs                                                     ┃
    ┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
    │ prox-6db7c6dc9b-l42v4 │ 127.0.0.1/8, 172.17.0.4/16, 127.0.0.1, 172.17.0.4, 172.17.255.255 │
    └───────────────────────┴───────────────────────────────────────────────────────────────────┘

    DEPLOYMENT DETAILS

    ┏━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
    ┃ NAME      ┃ Type     ┃ CLUSTER-IP    ┃ EXTERNAL-IP ┃ PORT(S)        ┃
    ┡━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
    │ proxchart │ NodePort │ 10.103.156.83 │ {}          │ 8081:31036/TCP │
    └───────────┴──────────┴───────────────┴─────────────┴────────────────┘

********************
Future Enhancements
********************

In future, more information can be extracted by adding new functions to the file. The process of getting interfaces using regex can be made more proficient.