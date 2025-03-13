pipeline {
    agent any

    environment {
        ALLURE_RESULTS_DIR = 'allure-results'
    }

    stages {

        stage('Build and Start Services') {
            steps {
                script {
                    // Задаем переменную MY_APP_DIR 
                    env.MY_APP_DIR = "/var/lib/docker/volumes/jenkins-data-flask/_data/workspace/${env.JOB_NAME}"
                    echo "MY_APP_DIR is ${env.MY_APP_DIR}"
                    // Выполняем команду в оболочке; переменная MY_APP_DIR будет доступна благодаря env.
                    sh """
                        echo "Using MY_APP_DIR: \$MY_APP_DIR"
                        docker compose up --build web db -d
                    """
                }
            }
        }
        stage('Run Tests') {
            steps {
                script {
                    // Создаем директорию для результатов
                    sh "mkdir -p ${env.ALLURE_RESULTS_DIR}"
                    // Запускаем тестовый сервис; переменная ALLURE_RESULTS_DIR будет доступна
                    sh "docker compose run --rm -e TEST_PATH=tests/ -e TEST_ARGS='--alluredir=${env.ALLURE_RESULTS_DIR}' test"
                }
            }
        }
    }

    post {
        always {
            script {
                def resultsExist = sh(returnStatus: true, script: """
                    [ -d ${env.ALLURE_RESULTS_DIR} ] && [ \"\$(ls -A ${env.ALLURE_RESULTS_DIR})\" ]
                """) == 0

                if (resultsExist) {
                    echo 'Allure results found. Generating report...'
                    allure([
                        includeProperties: false,
                        jdk: '',
                        properties: [],
                        reportBuildPolicy: 'ALWAYS',
                        results: [[path: "${env.ALLURE_RESULTS_DIR}"]]
                    ])
                } else {
                    echo 'No Allure results found. Tests might not have run.'
                }
            }
        }
        cleanup {
            echo 'Cleaning up...'
            sh """
            docker compose down
            rm -rf allure.zip ${env.ALLURE_RESULTS_DIR}
            """
            deleteDir()
        }
    }
}
