docker system prune -f

docker build -t flow-app-server-image ./server
docker build -t flow-app-client-image ./client

docker run -d -p 5000:5000 flow-app-server-image
docker run -d -p 4200:4200 flow-app-client-image

docker run -d -p 4200:4200 -e BACKEND_URL=https://flow-app-server-cbxodu5vga-uc.a.run.app flow-app-client-image

docker-compose up -d
docker-compose up --build -d


Google Run:

gcloud init
gcloud auth login
gcloud auth configure-docker australia-southeast1-docker.pkg.dev
docker build -t flow-app-server-image ./server
docker tag flow-app-server-image australia-southeast1-docker.pkg.dev/flow-app-project-417300/flow-app-repository/flow-app-server-image
docker push australia-southeast1-docker.pkg.dev/flow-app-project-417300/flow-app-repository/flow-app-server-image






