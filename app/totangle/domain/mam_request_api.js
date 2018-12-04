const generate = require('iota-generate-seed')
var BodyParser = require('body-parser')
var Http = require('http'),
  Router = require('router'),
  server,
  router;
router = new Router();

var content = ''
var seed_seed = ''
var startCount = 0

const Mam = require('./lib/mam.client.js')
const {
  asciiToTrytes,
  trytesToAscii
} = require('@iota/converter')

let root = ''
let mamState

async function MAM_init () {
  const seed = generate()
  mamState = await Mam.init('http://node.deviceproof.org:14266',seed)
  return seed
}

async function MAM_init_update () {
  mamState = await Mam.init('http://node.deviceproof.org:14266', seed_seed)
  console.log(+startCount)
  mamState.channel.start = +startCount
}

const publish = async packet => {
  const trytes = asciiToTrytes(JSON.stringify(packet))
  const message = Mam.create(mamState, trytes)
  mamState = message.state
  console.log(message)
  await Mam.attach(message.payload, message.address)
  return message.root
}

const logData = data => {
  console.log(JSON.parse(trytesToAscii(data)))
}

const execute = async message => {
  root = await publish(message)
  const resp = await Mam.fetch(root, 'public', null, logData)
  return root
}

const _logData = data => {
  content = JSON.parse(trytesToAscii(data))
}

const listen = async domain_root => {
  const resp = await Mam.fetch(domain_root, 'public', null, _logData)
  const _content = content
  content = ''
  console.log(_content)
  return JSON.stringify(_content)
}

server = Http.createServer(function (request, response) {
  router(request, response, function (error) {
    if (!error) {
      response.writeHead(404);
    } else {
      console.log(error.message, error.stack);
      response.writeHead(400);
    }
    response.end('RESTful API Server is running!');
  });
});

server.listen(3000, function () {
  console.log('Listening on port 3000');
});

router.use(BodyParser.text());
router.use(BodyParser.json());

async function domain_register(request, response) {
  const seed = await MAM_init()
  const root = await execute(request.body)
  //console.log(root,seed);
  response.writeHead(201, {
    'Content-Type': 'application/json'
  });
  console.log(root,seed)
  response.end(root)
}
router.post('/reg', domain_register);

async function seed_getter(request, response) {
  const mam_seed = mamState.seed
  console.log(mam_seed)
  response.end(mam_seed)
}
router.post('/seed', seed_getter);

async function domain_update(request, response) {
  await MAM_init_update()
  const root = await execute(request.body)
  response.writeHead(201, {
    'Content-Type': 'application/json'
  });
  console.log(root)
  console.log(" ")
  response.end(root)
  
}
router.post('/update', domain_update);

async function send_index(request, response) {
  startCount = request.body
  console.log(startCount)
  response.end(startCount)
}
router.post('/index', send_index);

async function send_seed(request, response) {
  console.log(request.body)
  seed_seed = request.body
  response.end(seed_seed)
}
router.post('/seed1', send_seed);


async function domain_search(request, response) {
  const seed = await MAM_init()
  const content = await listen(request.body)
  console.log(content);
  response.writeHead(201, {
    'Content-Type': 'text/plain'
  });
  response.end(content);
}
router.post('/search', domain_search);