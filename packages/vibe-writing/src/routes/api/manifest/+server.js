import { json } from '@sveltejs/kit';
import fs from 'fs';
import path from 'path';

export async function GET() {
	// Correctly read the file from the static directory
	const filePath = path.resolve('static/vibe.json');
	try {
		const fileContents = fs.readFileSync(filePath, 'utf-8');
		const manifest = JSON.parse(fileContents);
		return json(manifest);
	} catch (e) {
		console.error('Failed to read or parse manifest file:', e);
		return json({ message: 'Internal Error: Could not read manifest file.' }, { status: 500 });
	}
}
