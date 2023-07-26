wrk.method = "POST"
wrk.headers["Content-Type"] = "application/json"
wrk.headers["Rate-Limiter-Flag"] = RATE_LIMITER_FLAG
wrk.body = '{"email": "mikhailkrasovitskiy@gmail.com"}'

local counter = 1

function response(status, headers, body)
   print("Response Body:", body)

   if counter == 4 then
      wrk.thread:stop()
   end
   counter = counter + 1
end
