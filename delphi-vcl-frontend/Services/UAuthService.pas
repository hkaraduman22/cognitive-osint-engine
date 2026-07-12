unit UAuthService;

interface

uses
  System.SysUtils;

type
  EAuthServiceError = class(Exception);

  TAuthResult = record
    AccessToken: string;
    RefreshToken: string;
  end;

  TAuthService = class
  private
    function RequestTokens(const AEndpoint, AUsername, APassword: string): TAuthResult;
    function ParseTokenResponse(const AJsonText: string): TAuthResult;
  public
    function Login(const AUsername, APassword: string): TAuthResult;
    function Register(const AUsername, APassword: string): TAuthResult;
    /// <summary>Suresi dolmak uzere olan/dolmus bir access token'i, sakli refresh token ile yeniler.</summary>
    function Refresh(const ARefreshToken: string): TAuthResult;
    /// <summary>Sunucu tarafinda refresh token'i iptal eder (204 bekler).</summary>
    procedure Logout(const ARefreshToken: string);
  end;

implementation

uses
  System.JSON,
  System.Net.HttpClient,
  UHttpApiClient;

function TAuthService.ParseTokenResponse(const AJsonText: string): TAuthResult;
var
  LJsonValue: TJSONValue;
  LAccessValue, LRefreshValue: TJSONValue;
begin
  LJsonValue := TJSONObject.ParseJSONValue(AJsonText);
  try
    if not (LJsonValue is TJSONObject) then
      raise EAuthServiceError.Create('Sunucu yaniti gecersiz.');

    LAccessValue := TJSONObject(LJsonValue).GetValue('access_token');
    if not Assigned(LAccessValue) then
      raise EAuthServiceError.Create('access_token alani bulunamadi.');

    Result.AccessToken := Trim(LAccessValue.Value);
    if Result.AccessToken = '' then
      raise EAuthServiceError.Create('access_token bos geldi.');

    LRefreshValue := TJSONObject(LJsonValue).GetValue('refresh_token');
    if Assigned(LRefreshValue) then
      Result.RefreshToken := Trim(LRefreshValue.Value)
    else
      Result.RefreshToken := '';
  finally
    LJsonValue.Free;
  end;
end;

function TAuthService.RequestTokens(const AEndpoint, AUsername, APassword: string): TAuthResult;
var
  LClient: THttpApiClient;
  LBody: TJSONObject;
  LResponse: IHTTPResponse;
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

    Result := ParseTokenResponse(LResponse.ContentAsString(TEncoding.UTF8));
  finally
    LClient.Free;
  end;
end;

function TAuthService.Login(const AUsername, APassword: string): TAuthResult;
begin
  Result := RequestTokens('/auth/login', AUsername, APassword);
end;

function TAuthService.Register(const AUsername, APassword: string): TAuthResult;
begin
  Result := RequestTokens('/auth/register', AUsername, APassword);
end;

function TAuthService.Refresh(const ARefreshToken: string): TAuthResult;
var
  LClient: THttpApiClient;
  LBody: TJSONObject;
  LResponse: IHTTPResponse;
begin
  if Trim(ARefreshToken) = '' then
    raise EAuthServiceError.Create('Refresh token bos olamaz.');

  LClient := THttpApiClient.Create;
  try
    LBody := TJSONObject.Create;
    try
      LBody.AddPair('refresh_token', ARefreshToken);
      LResponse := LClient.PostJson('/auth/refresh', LBody);
    finally
      LBody.Free;
    end;

    if LResponse.StatusCode <> 200 then
      raise EAuthServiceError.CreateFmt('Oturum yenileme basarisiz. HTTP %d', [LResponse.StatusCode]);

    Result := ParseTokenResponse(LResponse.ContentAsString(TEncoding.UTF8));
  finally
    LClient.Free;
  end;
end;

procedure TAuthService.Logout(const ARefreshToken: string);
var
  LClient: THttpApiClient;
  LBody: TJSONObject;
begin
  if Trim(ARefreshToken) = '' then
    Exit;

  LClient := THttpApiClient.Create;
  try
    LBody := TJSONObject.Create;
    try
      LBody.AddPair('refresh_token', ARefreshToken);
      // Sunucu tarafi cikis islemi en iyi caba (best-effort) ile yapilir;
      // basarisiz olsa bile yerel oturum temizligini engellememelidir.
      try
        LClient.PostJson('/auth/logout', LBody);
      except
        // Aginin coktugu/sunucunun kapali oldugu durumlarda bile kullanici
        // yerelde cikis yapabilmeli - hata burada yutulur.
      end;
    finally
      LBody.Free;
    end;
  finally
    LClient.Free;
  end;
end;

end.
