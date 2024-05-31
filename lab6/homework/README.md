# How it works?

```
python doctor.py <doctor_name>
python technician.py <technician_name> <exam_types>, where exam_types is either elbow, knee or hip. To pass two or more exams, wrte it without space after comma
python admin.py
```

#### Connecting
1. For each doctor create exchange "hospital", queue for results, queue for admin info
2. For each technician create exchange "hospital", queues for exam_types done by this technician, queue for admin info
3. For admin create exchange "hospital", queue for admin

When creating a queue, we also bind it to exchange and specific routing_key. Consequently, when information with exact routing_key will be provided, exchange will know where to give that message.
 
#### Doctor has patient
1. After providing details about a patient, create routing_key with exam_type.
   
    - publish info on exchange with created routing_key. Exchange will route this information based on provided key.
    - accordingly, publish info to admin using different routing_key
   
2. Both technician and admin listen to messages all the time.

#### Admin sends a message
1. Admin sends message with the same routing_key as queues created specifically for this purpose.

