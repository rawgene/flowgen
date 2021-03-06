# Copyright 2019 Alessandro Pio Greco, Patrick Hedley-Miller, Filipe Jesus, Zeyu Yang

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from configparser import ConfigParser
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from uuid import UUID
import subprocess
from zipfile import ZipFile
import json

if __name__ == "__main__":
    # change current working directory to project root
    root = os.path.realpath(os.path.join(os.path.dirname(__file__), '../..' ))
    os.chdir(root)

    # read config file
    config = ConfigParser()
    config.read("config.ini")
    database = config.get("main", "database")

    Base = automap_base()
    engine = create_engine(database)
    Base.prepare(engine, reflect=True)
    RSession = Base.classes.analysis_session
    Queue = Base.classes.analysis_queue
    session = Session(engine)

    query = session.query(RSession, Queue).filter(Queue.status == 1)\
                    .filter(RSession.id == Queue.session_id).all()
    if len(query) > 0:
        s, q = query[0]
        queue_id = q.id
        session_id = s.id
        identifier = UUID(s.identifier)
        if q.jobtype == "index":
            logpath = f"{root}/Data/{identifier}/indexing.log"
            outdir = f"{root}/Data/{identifier}/genome"
        elif q.jobtype == "workflow":
            logpath = f"{root}/Data/{identifier}/workflow.log"
            outdir = f"{root}/Data/{identifier}/output"
        logfile = open(logpath, "a+")
        q.status = 0
        q.result = "submitted"
        session.commit()
        cwl = q.cwl
        yml = q.yml
        session.close()
        proc = subprocess.run(["cwl-runner",
                                f"--outdir={outdir}",
                                "--timestamp",
                                "--tmpdir-prefix=/tmp/",
                                "--tmp-outdir-prefix=/tmp/",
                                cwl,
                                yml],
                                stdout=logfile, stderr=logfile)

        Base = automap_base()
        engine = create_engine(database)
        Base.prepare(engine, reflect=True)
        Queue = Base.classes.analysis_queue
        session = Session(engine)
        Workflow = Base.classes.analysis_workflow
        q = session.query(Queue).filter(Queue.id == queue_id).first()
        if proc.returncode == 0:
            q.status = 0
            q.result = "success"
            workflows = session.query(Workflow).filter(Workflow.session_id == session_id).all()
            os.chdir(f"Data/{identifier}/output")
            with ZipFile("../results.zip", "w") as result:
                for wf in workflows:
                    paths = json.loads(wf.paths)
                    for k,v in paths.items():
                        for path in v:
                            result.write(path.split("output/")[-1])

        else:
            q.status = 0
            q.result = "failed"
        
        session.commit()
        session.close()
        logfile.close()
