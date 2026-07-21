unit UAdminService;

interface

uses
  System.SysUtils;

type
  EAdminServiceError = class(Exception);

  TAdminUserItem = record
    Id: Integer;
    Username: string;
    Email: string;
    IsAdmin: Boolean;
    CreatedAt: string;
  end;

  TAdminUserItems = TArray<TAdminUserItem>;

  TAdminUserSearchHistoryItem = record
    SearchHistoryId: Integer;
    Query: string;
    Status: string;
    CompanyCount: Integer;
    CreatedAt: string;
  end;

  TAdminUserSearchHistoryItems = TArray<TAdminUserSearchHistoryItem>;

  TAdminService = class
  public
    function GetUsers(const ABearerToken: string): TAdminUserItems;
    function GetUserSearchHistory(const ABearerToken: string; const AUserId: Integer): TAdminUserSearchHistoryItems;
  end;

implementation

uses
  System.JSON,
  System.Net.HttpClient,
  UHttpApiClient;

function JsonGetString(const AObject: TJSONObject; const AName: string): string;
var
  LValue: TJSONValue;
begin
  LValue := AObject.GetValue(AName);
  if Assigned(LValue) then
    Result := Trim(LValue.Value)
  else
    Result := '';
end;

function JsonGetInt(const AObject: TJSONObject; const AName: string; const ADefault: Integer): Integer;
var
  LValue: TJSONValue;
begin
  LValue := AObject.GetValue(AName);
  if not Assigned(LValue) then
    Exit(ADefault);

  if LValue is TJSONNumber then
    Exit(TJSONNumber(LValue).AsInt);

  Result := StrToIntDef(Trim(LValue.Value), ADefault);
end;

function JsonGetBool(const AObject: TJSONObject; const AName: string; const ADefault: Boolean): Boolean;
var
  LValue: TJSONValue;
  LText: string;
begin
  LValue := AObject.GetValue(AName);
  if not Assigned(LValue) then
    Exit(ADefault);

  if LValue is TJSONBool then
    Exit(TJSONBool(LValue).AsBoolean);

  LText := LowerCase(Trim(LValue.Value));
  if (LText = 'true') or (LText = '1') then
    Exit(True);
  if (LText = 'false') or (LText = '0') then
    Exit(False);

  Result := ADefault;
end;

function TAdminService.GetUsers(const ABearerToken: string): TAdminUserItems;
var
  LClient: THttpApiClient;
  LResponse: IHTTPResponse;
  LJsonValue: TJSONValue;
  LArray: TJSONArray;
  LObj: TJSONObject;
  I: Integer;
begin
  if Trim(ABearerToken) = '' then
    raise EAdminServiceError.Create('JWT token bulunamadi.');

  LClient := THttpApiClient.Create;
  try
    LResponse := LClient.Get('/api/v1/admin/users', ABearerToken);
    if (LResponse.StatusCode < 200) or (LResponse.StatusCode >= 300) then
      raise EAdminServiceError.CreateFmt('Admin users basarisiz. HTTP %d', [LResponse.StatusCode]);

    LJsonValue := TJSONObject.ParseJSONValue(LResponse.ContentAsString(TEncoding.UTF8));
    try
      if not (LJsonValue is TJSONArray) then
        raise EAdminServiceError.Create('Admin users yaniti dizi formatinda degil.');

      LArray := TJSONArray(LJsonValue);
      SetLength(Result, LArray.Count);

      for I := 0 to LArray.Count - 1 do
      begin
        if not (LArray.Items[I] is TJSONObject) then
          raise EAdminServiceError.Create('Admin users kayit formati gecersiz.');

        LObj := TJSONObject(LArray.Items[I]);
        Result[I].Id := JsonGetInt(LObj, 'id', 0);
        Result[I].Username := JsonGetString(LObj, 'username');
        Result[I].Email := JsonGetString(LObj, 'email');
        Result[I].IsAdmin := JsonGetBool(LObj, 'is_admin', False);
        Result[I].CreatedAt := JsonGetString(LObj, 'created_at');
      end;
    finally
      LJsonValue.Free;
    end;
  finally
    LClient.Free;
  end;
end;

function TAdminService.GetUserSearchHistory(const ABearerToken: string; const AUserId: Integer): TAdminUserSearchHistoryItems;
var
  LClient: THttpApiClient;
  LResponse: IHTTPResponse;
  LJsonValue: TJSONValue;
  LArray: TJSONArray;
  LObj: TJSONObject;
  I: Integer;
begin
  if Trim(ABearerToken) = '' then
    raise EAdminServiceError.Create('JWT token bulunamadi.');

  if AUserId <= 0 then
    raise EAdminServiceError.Create('Kullanici ID gecersiz.');

  LClient := THttpApiClient.Create;
  try
    LResponse := LClient.Get('/api/v1/admin/users/' + IntToStr(AUserId) + '/search-history', ABearerToken);
    if (LResponse.StatusCode < 200) or (LResponse.StatusCode >= 300) then
      raise EAdminServiceError.CreateFmt('Admin search history basarisiz. HTTP %d', [LResponse.StatusCode]);

    LJsonValue := TJSONObject.ParseJSONValue(LResponse.ContentAsString(TEncoding.UTF8));
    try
      if not (LJsonValue is TJSONArray) then
        raise EAdminServiceError.Create('Admin search history yaniti dizi formatinda degil.');

      LArray := TJSONArray(LJsonValue);
      SetLength(Result, LArray.Count);

      for I := 0 to LArray.Count - 1 do
      begin
        if not (LArray.Items[I] is TJSONObject) then
          raise EAdminServiceError.Create('Admin search history kayit formati gecersiz.');

        LObj := TJSONObject(LArray.Items[I]);
        Result[I].SearchHistoryId := JsonGetInt(LObj, 'search_history_id', 0);
        Result[I].Query := JsonGetString(LObj, 'query');
        Result[I].Status := JsonGetString(LObj, 'status');
        Result[I].CompanyCount := JsonGetInt(LObj, 'company_count', 0);
        Result[I].CreatedAt := JsonGetString(LObj, 'created_at');
      end;
    finally
      LJsonValue.Free;
    end;
  finally
    LClient.Free;
  end;
end;

end.
