def py(String args) {
    if (isUnix()) {
        sh "\"${env.WORKSPACE}/.venv-ci/bin/python\" ${args}"
    } else {
        bat "\"${env.WORKSPACE}\\.venv\\Scripts\\python.exe\" ${args}"
    }
}

pipeline {
    agent any

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timeout(time: 45, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    environment {
        HEADLESS        = '1'
        XRAY_TEST_PLAN  = 'WT-65'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    if (isUnix()) {
                        sh 'git rev-parse --short HEAD'
                    } else {
                        bat 'git rev-parse --short HEAD'
                    }
                }
            }
        }

        stage('Install dependencies') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'python3 -m venv .venv-ci'
                        sh '.venv-ci/bin/python -m pip install --upgrade pip'
                        sh '.venv-ci/bin/python -m pip install -r webtours-tests/requirements.txt'
                    } else {
                        bat '''
                            if not exist .venv ( python -m venv .venv )
                            .venv\\Scripts\\python -m pip install --upgrade pip
                            .venv\\Scripts\\python -m pip install -r webtours-tests\\requirements.txt
                        '''
                    }
                }
            }
        }

        stage('Check application is up') {
            steps {
                retry(3) {
                    script { py('scripts/check_app.py') }
                }
            }
        }

        stage('Run Selenium test suite') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    dir('webtours-tests') {
                        script { py('-m pytest') }
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
                        script { py("scripts/results_to_xray.py --plan ${env.XRAY_TEST_PLAN}") }
                    }
                }
            }
        }

        stage('Generate execution report') {
            steps {
                script { py('scripts/make_report.py') }
            }
        }
    }

    post {
        always {
            junit testResults: 'webtours-tests/reports/junit.xml', allowEmptyResults: true
            publishHTML(target: [
                reportDir: 'webtours-tests/reports',
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportFiles: 'report.html',
                reportName: 'Rapport PyTest Web Tours'
            ])
            archiveArtifacts artifacts: 'webtours-tests/reports/**', allowEmptyArchive: true
        }
    }
}
