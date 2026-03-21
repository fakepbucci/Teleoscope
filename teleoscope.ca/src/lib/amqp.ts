import amqp, { Connection, Channel } from 'amqplib';
import { v4 as uuidv4 } from 'uuid';

const username = process.env.RABBITMQ_USERNAME
const password = process.env.RABBITMQ_PASSWORD
const host = process.env.RABBITMQ_HOST
const port = process.env.RABBITMQ_PORT
const vhost = process.env.RABBITMQ_VHOST
const database = process.env.MONGODB_DATABASE

const rabbitMqUrl = `amqp://${username}:${password}@${host}:${port}/${vhost}`

let connection: Connection | null = null;
let channel: Channel | null = null;

async function getChannel(): Promise<Channel> {
    if (channel) {
        return channel;
    }

    connection = await amqp.connect(rabbitMqUrl);

    connection.on('close', () => {
        connection = null;
        channel = null;
    });

    connection.on('error', () => {
        connection = null;
        channel = null;
    });

    channel = await connection.createChannel();

    channel.on('close', () => {
        channel = null;
    });

    channel.on('error', () => {
        channel = null;
    });

    return channel;
}

async function send(task: string, args: any) {
    const queue = `${process.env.RABBITMQ_QUEUE}`;

    const kwargs = {
        ...args,
        database: database
    }

    const ch = await getChannel();

    await ch.assertQueue(queue, {
        durable: true
    });

    const message = {
        id: uuidv4(),
        task: task,
        args: kwargs,
        kwargs: kwargs,
        retries: 0,
        eta: new Date().toISOString()
    };

    const msg = JSON.stringify(message)

    ch.sendToQueue(queue, Buffer.from(msg));
}

export default send;
