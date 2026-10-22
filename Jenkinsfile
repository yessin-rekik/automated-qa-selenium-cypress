pipeline {
    agent { label 'windows' }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timeout(time: 45, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    environment {
        WEBTOURS_URL    = 'http://127.0.0.1:1080/WebTours/index.htm'
        WEBTOURS_CGI    = 'http://127.0.0.1:1080/cgi-bin'
        HEADLESS        = '1'
        XRAY_TEST_PLAN  = 'WT-65'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                bat 'git rev-parse --short HEAD'
            }
        }

        stage('Install dependencies') {
            steps {
                bat '''
                    if not exist .venv ( python -m venv .venv )
                    .venv\\Scripts\\python -m pip install --upgrade pip
                    .venv\\Scripts\\python -m pip install -r webtours-tests\\requirements.txt
                '''
            }
        }

        stage('Check application is up') {
            steps {
                retry(3) {
                    bat '.venv\\Scripts\\python -c "import os,requests; r=requests.get(os.environ[\'WEBTOURS_URL\'], timeout=10); print(\'HTTP\', r.status_code); assert r.status_code == 200"'
                }
            }
        }

        stage('Run Selenium test suite') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    dir('webtours-tests') {
                        bat '..\\.venv\\Scripts\\python -m pytest'
                    }
                }
            }
        }

        stage('Publish results to Xray') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    withCredentials([
                        string(credentialsId: 'xray-client-id', variable: 'XRAY_CLIENT_ID'),
                        string(credentialsId: 'xray-client-secret', variable: 'XRAY_CLIENT_SECRET')
                    ]) {
                        bat '.venv\\Scripts\\python scripts\\results_to_xray.py --plan %XRAY_TEST_PLAN%'
                    }
                }
            }
        }

        stage('Generate execution report') {
            steps {
                bat '.venv\\Scripts\\python scripts\\make_report.py'
            }
        }
    }

    post {
        always {
            junit 'webtours-tests/reports/junit.xml'
            publishHTML(target: [
                reportDir: 'webtours-tests/reports',
                reportFiles: 'report.html',
                reportName: 'Rapport PyTest Web Tours'
            ])
            archiveArtifacts artifacts: 'webtours-tests/reports/**', allowEmptyArchive: true
        }
    }
}
