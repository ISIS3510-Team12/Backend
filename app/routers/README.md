## Routers
This folder is for all logic that is related to the API layer (the controller layer). This can include things like routers, endpoints, and other API related services that are used by the API layer.

Please try to avoid putting business logic in this layer, as it should be handled by the services layer. The routers should only handle the request and response, and delegate the business logic to the services layer.