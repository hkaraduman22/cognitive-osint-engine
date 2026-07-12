unit UAuthService;

interface

uses
  System.SysUtils;

type
  EAuthServiceError = class(Exception);

  TAuthService = class
  private
    function RequestToken(const AEndpoint, AUsername, APassword: string): string;
  public
    function Login(const AUsername, APassword: string): string;
    function Register(const AUsername, APassword: string): string;
  end;

implementation

uses
  System.JSON,
  System.Net.HttpClient,
  UHttpApiClient;

function TAuthService.RequestToken(const AEndpoint, AUsername, APassword: string): string;
var
  LClient: THttpApiClient;
  LBody: TJSONObject;
  LResponse: IHTTPResponse;
  LJsonValue: TJSONValue;
  LTokenValue: TJSONValue;
  LToken: string;
begin
  if Trim(AEndpoint) = '' then
    raise EAuthServiceError.Create('Endpoint bos olamaz.');

  if Trim(AUsername) = '' then
    raise EAuthServiceError.Create('Kullanici adi bos olamaz.');

  if Trim(APassword) = '' then
    raise EAuthServiceError.Create('Sifre bos olamaz.');

  LClient := THttpApiClient.Create;
  try
    LBody := TJSONObject.Create;
    try
      LBody.AddPair('username', AUsername);
      LBody.AddPair('password', APassword);
      LResponse := LClient.PostJson(AEndpoint, LBody);
    finally
      LBody.Free;
    end;

    if LResponse.StatusCode <> 200 then
      raise EAuthServiceError.CreateFmt('Islem basarisiz. HTTP %d', [LResponse.StatusCode]);

    LJsonValue := TJSONObject.ParseJSONValue(LResponse.ContentAsString(TEncoding.UTF8));
    try
      if not (LJsonValue is TJSONObject) then
        raise EAuthServiceError.Create('Sunucu yaniti gecersiz.');

      LTokenValue := TJSONObject(LJsonValue).GetValue('access_token');
      if not Assigned(LTokenValue) then
        raise EAuthServiceError.Create('access_token alani bulunamadi.');

      LToken := Trim(LTokenValue.Value);
      if LToken = '' then
        raise EAuthServiceError.Create('access_token bos geldi.');

      Result := LToken;
    finally
      LJsonValue.Free;
    end;
  finally
    LClient.Free;
  end;
end;

function TAuthService.Login(const AUsername, APassword: string): string;
begin
  Result := RequestToken('/auth/login', AUsername, APassword);
end;

function TAuthService.Register(const AUsername, APassword: string): string;
begin
  Result := RequestToken('/auth/register', AUsername, APassword);
end;

end.
