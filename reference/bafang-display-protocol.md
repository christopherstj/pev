The Bafang display protocol is a request/response protocol where the display  
sends the requests and the controller responds. It utilizes a trailing checksum  
and is full of inconsistencies.

## Serial Protocol

Rules:
* Read requests starts with 0x11
* Write requests starts with 0x16

The next byte is an opcode for the type of operation.

When checksum is present it is usually the sum of all previous bytes  
(excluding request type and opcode) truncated to 8 bits.


## Read Requests

### Read Status

**Request:**  
11 08

**Response:**  
XX

Where XX is a status code.

Code  | Description
----- | -----------
00    | OK
01    | Pedaling
02    | ?
03    | Brake activate


### Read Current

**Request**  
11 0A

**Response**  
XX CC

Where XX is current in amps x 2 and CC is checksum which is XX.






